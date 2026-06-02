import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
  Logger,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiParam,
  ApiQuery,
} from '@nestjs/swagger';
import { PaymentsService } from './payments.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { PaymentMethod, PaymentStatus } from './entities/payment.entity';

@ApiTags('payments')
@Controller('payments')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth('JWT-auth')
export class PaymentsController {
  private readonly logger = new Logger(PaymentsController.name);

  constructor(private readonly paymentsService: PaymentsService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create a new payment' })
  @ApiResponse({ status: 201, description: 'Payment created' })
  @ApiResponse({ status: 400, description: 'Invalid request' })
  async create(
    @Body()
    body: {
      listingId?: string;
      amount: number;
      currency?: string;
      method: PaymentMethod;
      description: string;
    },
    @CurrentUser() user: { id: string; email: string; firstName: string; lastName: string },
  ) {
    this.logger.log(`Creating payment for user: ${user.id}`);

    return this.paymentsService.create({
      userId: user.id,
      listingId: body.listingId,
      amount: body.amount,
      currency: body.currency,
      method: body.method,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      description: body.description,
    });
  }

  @Get()
  @ApiOperation({ summary: 'Get user payment history' })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiQuery({ name: 'offset', required: false, type: Number })
  @ApiQuery({ name: 'status', required: false, enum: PaymentStatus })
  @ApiResponse({ status: 200, description: 'Payment list' })
  async findAll(
    @CurrentUser() user: { id: string },
    @Query('limit') limit?: number,
    @Query('offset') offset?: number,
    @Query('status') status?: PaymentStatus,
  ) {
    return this.paymentsService.findByUser(user.id, { limit, offset, status });
  }

  @Get('stats')
  @ApiOperation({ summary: 'Get user payment statistics' })
  @ApiResponse({ status: 200, description: 'Payment stats' })
  async getStats(@CurrentUser() user: { id: string }) {
    return this.paymentsService.getPaymentStats(user.id);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get payment by ID' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Payment details' })
  @ApiResponse({ status: 404, description: 'Payment not found' })
  async findOne(@Param('id') id: string) {
    return this.paymentsService.findByIdOrFail(id);
  }

  @Post(':id/refund')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Refund a payment' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Payment refunded' })
  @ApiResponse({ status: 400, description: 'Cannot refund payment' })
  @ApiResponse({ status: 404, description: 'Payment not found' })
  async refund(
    @Param('id') id: string,
    @Body() body: { reason?: string },
  ) {
    this.logger.log(`Processing refund for payment: ${id}`);
    return this.paymentsService.refund(id, body.reason);
  }
}