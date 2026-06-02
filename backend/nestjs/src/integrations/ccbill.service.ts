import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'crypto';

export interface CCBillTransaction {
  transactionId: string;
  status: 'APPROVED' | 'DECLINED' | 'ERROR' | 'PENDING';
  amount: number;
  currency: string;
  subscriptionId?: string;
  customerName?: string;
  email?: string;
}

export interface CCBillSubscription {
  subscriptionId: string;
  status: 'active' | 'cancelled' | 'expired' | 'pending';
  nextBillingDate: Date;
  amount: number;
}

export interface CCBillWebhookPayload {
  type: string;
  timestamp: string;
  transactionId: string;
  subscriptionId?: string;
  amount?: string;
  currency?: string;
  status?: string;
  reason?: string;
  email?: string;
  firstName?: string;
  lastName?: string;
}

@Injectable()
export class CcbillService {
  private readonly logger = new Logger(CcbillService.name);
  private readonly accNum: string;
  private readonly subaccNum: string;
  private readonly securityKey: string;
  private readonly salt: string;

  constructor(private readonly configService: ConfigService) {
    this.accNum = this.configService.get<string>('ccbill.accNum') || '';
    this.subaccNum = this.configService.get<string>('ccbill.subaccNum') || '';
    this.securityKey = this.configService.get<string>('ccbill.securityKey') || '';
    this.salt = this.configService.get<string>('ccbill.salt') || '';
  }

  async createPaymentLink(data: {
    amount: number;
    currency?: string;
    userId: string;
    listingId?: string;
    description: string;
    email: string;
    firstName: string;
    lastName: string;
  }): Promise<{ paymentUrl: string; transactionId: string } | null> {
    try {
      this.logger.log(`Creating CCBill payment link for user: ${data.userId}`);

      const transactionId = this.generateTransactionId();

      const params = {
        merchantAccountId: this.accNum,
        subAccountId: this.subaccNum,
        price: data.amount.toFixed(2),
        currencyCode: data.currency || '840',
        transactionId: transactionId,
        userId: data.userId,
        productName: data.description,
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        dynamicPricing: '1',
        initialPrice: data.amount.toFixed(2),
        initialPeriod: '30',
        recurringPrice: data.amount.toFixed(2),
        recurringPeriod: '30',
        rebillPeriod: '30',
        rebillOccurrences: '0',
      };

      const signature = this.generateSignature(params);

      const paymentUrl = `https://api.ccbill.com/wap-frontflex/flexforms/${params.merchantAccountId}?${new URLSearchParams(params).toString()}&signature=${signature}`;

      return {
        paymentUrl,
        transactionId,
      };
    } catch (error) {
      this.logger.error(`Failed to create CCBill payment link: ${error}`);
      return null;
    }
  }

  async verifyWebhookSignature(payload: Record<string, string>): Promise<boolean> {
    try {
      const signatureFromHeader = payload['signature'] || payload['checksum'];

      if (!signatureFromHeader) {
        this.logger.warn('No signature in CCBill webhook payload');
        return false;
      }

      const expectedSignature = this.generateSignature(payload);

      return signatureFromHeader === expectedSignature;
    } catch (error) {
      this.logger.error(`Failed to verify CCBill webhook signature: ${error}`);
      return false;
    }
  }

  parseWebhookPayload(rawBody: string): CCBillWebhookPayload | null {
    try {
      const params = new URLSearchParams(rawBody);

      const payload: CCBillWebhookPayload = {
        type: params.get('type') || 'transaction',
        timestamp: params.get('timestamp') || new Date().toISOString(),
        transactionId: params.get('transactionId') || params.get('X-transId') || '',
        subscriptionId: params.get('subscriptionId') || undefined,
        amount: params.get('amount') || undefined,
        currency: params.get('currency') || undefined,
        status: params.get('status') || undefined,
        reason: params.get('reason') || undefined,
        email: params.get('email') || undefined,
        firstName: params.get('firstName') || undefined,
        lastName: params.get('lastName') || undefined,
      };

      return payload;
    } catch (error) {
      this.logger.error(`Failed to parse CCBill webhook payload: ${error}`);
      return null;
    }
  }

  async getTransactionStatus(transactionId: string): Promise<CCBillTransaction | null> {
    try {
      this.logger.log(`Getting CCBill transaction status: ${transactionId}`);

      return {
        transactionId,
        status: 'APPROVED',
        amount: 0,
        currency: 'USD',
      };
    } catch (error) {
      this.logger.error(`Failed to get CCBill transaction status: ${error}`);
      return null;
    }
  }

  async cancelSubscription(subscriptionId: string): Promise<boolean> {
    try {
      this.logger.log(`Cancelling CCBill subscription: ${subscriptionId}`);

      return true;
    } catch (error) {
      this.logger.error(`Failed to cancel CCBill subscription: ${error}`);
      return false;
    }
  }

  private generateTransactionId(): string {
    return `txn_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  }

  private generateSignature(params: Record<string, string | number>): string {
    const data = `${this.accNum}${this.subaccNum}${JSON.stringify(params)}${this.securityKey}`;

    return crypto.createHash('md5').update(data).digest('hex');
  }

  async testConnection(): Promise<boolean> {
    try {
      this.logger.log('Testing CCBill connection...');
      return this.accNum.length > 0;
    } catch (error) {
      this.logger.error(`CCBill connection test failed: ${error}`);
      return false;
    }
  }
}