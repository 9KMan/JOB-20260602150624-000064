import {
  Injectable,
  NotFoundException,
  BadRequestException,
  Logger,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Payment, PaymentStatus, PaymentMethod } from './entities/payment.entity';
import { CcbillService } from '../integrations/ccbill.service';

export interface CreatePaymentDto {
  userId: string;
  listingId?: string;
  amount: number;
  currency?: string;
  method: PaymentMethod;
  email: string;
  firstName: string;
  lastName: string;
  description: string;
}

@Injectable()
export class PaymentsService {
  private readonly logger = new Logger(PaymentsService.name);

  constructor(
    @InjectRepository(Payment)
    private readonly paymentRepository: Repository<Payment>,
    private readonly ccbillService: CcbillService,
  ) {}

  async create(createPaymentDto: CreatePaymentDto): Promise<{
    payment: Payment;
    paymentUrl?: string;
  }> {
    const payment = this.paymentRepository.create({
      userId: createPaymentDto.userId,
      listingId: createPaymentDto.listingId || null,
      amount: createPaymentDto.amount,
      currency: createPaymentDto.currency || 'USD',
      status: PaymentStatus.PENDING,
      method: createPaymentDto.method,
    });

    const savedPayment = await this.paymentRepository.save(payment);

    let paymentUrl: string | undefined;

    if (createPaymentDto.method === PaymentMethod.CCBILL) {
      const ccbillLink = await this.ccbillService.createPaymentLink({
        amount: createPaymentDto.amount,
        userId: createPaymentDto.userId,
        listingId: createPaymentDto.listingId,
        description: createPaymentDto.description,
        email: createPaymentDto.email,
        firstName: createPaymentDto.firstName,
        lastName: createPaymentDto.lastName,
      });

      if (ccbillLink) {
        savedPayment.externalTransactionId = ccbillLink.transactionId;
        await this.paymentRepository.save(savedPayment);
        paymentUrl = ccbillLink.paymentUrl;
      }
    }

    this.logger.log(`Payment created: ${savedPayment.id} for user ${savedPayment.userId}`);

    return { payment: savedPayment, paymentUrl };
  }

  async findById(id: string): Promise<Payment | null> {
    return this.paymentRepository.findOne({
      where: { id },
      relations: [],
    });
  }

  async findByIdOrFail(id: string): Promise<Payment> {
    const payment = await this.findById(id);

    if (!payment) {
      throw new NotFoundException(`Payment with ID ${id} not found`);
    }

    return payment;
  }

  async findByUser(userId: string, options?: {
    limit?: number;
    offset?: number;
    status?: PaymentStatus;
  }): Promise<{ payments: Payment[]; total: number }> {
    const { limit = 20, offset = 0, status } = options ?? {};

    const queryBuilder = this.paymentRepository
      .createQueryBuilder('payment')
      .where('payment.userId = :userId', { userId });

    if (status) {
      queryBuilder.andWhere('payment.status = :status', { status });
    }

    const [payments, total] = await queryBuilder
      .orderBy('payment.createdAt', 'DESC')
      .skip(offset)
      .take(limit)
      .getManyAndCount();

    return { payments, total };
  }

  async findByTransactionId(externalTransactionId: string): Promise<Payment | null> {
    return this.paymentRepository.findOne({
      where: { externalTransactionId },
    });
  }

  async updateStatus(
    id: string,
    status: PaymentStatus,
    externalTransactionId?: string,
    metadata?: Record<string, unknown>,
  ): Promise<Payment> {
    const payment = await this.findByIdOrFail(id);

    payment.status = status;

    if (externalTransactionId) {
      payment.externalTransactionId = externalTransactionId;
    }

    if (metadata) {
      payment.metadata = { ...payment.metadata, ...metadata };
    }

    if (status === PaymentStatus.COMPLETED) {
      payment.paymentIntentId = externalTransactionId || payment.paymentIntentId;
    }

    if (status === PaymentStatus.FAILED && metadata?.['reason']) {
      payment.failureReason = metadata['reason'] as string;
    }

    return this.paymentRepository.save(payment);
  }

  async processWebhook(transactionId: string, status: string, metadata?: Record<string, unknown>): Promise<void> {
    const payment = await this.findByTransactionId(transactionId);

    if (!payment) {
      this.logger.warn(`Payment not found for transaction: ${transactionId}`);
      return;
    }

    let newStatus: PaymentStatus;

    switch (status.toUpperCase()) {
      case 'APPROVED':
      case 'COMPLETE':
        newStatus = PaymentStatus.COMPLETED;
        break;
      case 'DECLINED':
      case 'FAILED':
        newStatus = PaymentStatus.FAILED;
        break;
      case 'PENDING':
        newStatus = PaymentStatus.PROCESSING;
        break;
      case 'REFUNDED':
        newStatus = PaymentStatus.REFUNDED;
        break;
      default:
        newStatus = PaymentStatus.PENDING;
    }

    await this.updateStatus(payment.id, newStatus, transactionId, metadata);

    this.logger.log(`Payment ${payment.id} status updated to ${newStatus}`);
  }

  async refund(id: string, reason?: string): Promise<Payment> {
    const payment = await this.findByIdOrFail(id);

    if (payment.status !== PaymentStatus.COMPLETED) {
      throw new BadRequestException('Only completed payments can be refunded');
    }

    payment.status = PaymentStatus.REFUNDED;
    payment.metadata = { ...payment.metadata, refundReason: reason };

    const updatedPayment = await this.paymentRepository.save(payment);

    this.logger.log(`Payment ${id} refunded. Reason: ${reason}`);

    return updatedPayment;
  }

  async getPaymentStats(userId: string): Promise<{
    totalPayments: number;
    totalAmount: number;
    completedPayments: number;
    pendingPayments: number;
  }> {
    const result = await this.paymentRepository
      .createQueryBuilder('payment')
      .select('COUNT(*)', 'totalPayments')
      .addSelect('COALESCE(SUM(payment.amount), 0)', 'totalAmount')
      .where('payment.userId = :userId', { userId })
      .getRawOne();

    const completedCount = await this.paymentRepository.count({
      where: { userId, status: PaymentStatus.COMPLETED },
    });

    const pendingCount = await this.paymentRepository.count({
      where: { userId, status: PaymentStatus.PENDING },
    });

    return {
      totalPayments: parseInt(result['totalPayments'] || '0', 10),
      totalAmount: parseFloat(result['totalAmount'] || '0'),
      completedPayments: completedCount,
      pendingPayments: pendingCount,
    };
  }
}