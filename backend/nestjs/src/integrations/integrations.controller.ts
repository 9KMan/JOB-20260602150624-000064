import {
  Controller,
  Post,
  Body,
  Headers,
  RawBodyRequest,
  Req,
  HttpCode,
  HttpStatus,
  UseGuards,
  Logger,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiExcludeEndpoint,
} from '@nestjs/swagger';
import { YotiService } from './yoti.service';
import { PipedriveService } from './pipedrive.service';
import { CcbillService } from './ccbill.service';
import { ApiKeyGuard } from '../common/guards/api-key.guard';

@ApiTags('integrations')
@Controller('integrations')
export class IntegrationsController {
  private readonly logger = new Logger(IntegrationsController.name);

  constructor(
    private readonly yotiService: YotiService,
    private readonly pipedriveService: PipedriveService,
    private readonly ccbillService: CcbillService,
  ) {}

  @Post('yoti/webhook')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Yoti age verification webhook' })
  @ApiResponse({ status: 200, description: 'Webhook processed' })
  @ApiResponse({ status: 400, description: 'Invalid payload' })
  async handleYotiWebhook(
    @Body() payload: { sessionId: string; status: string },
  ): Promise<{ received: boolean }> {
    this.logger.log(`Yoti webhook received: ${JSON.stringify(payload)}`);

    if (payload.status === 'COMPLETED') {
      const result = await this.yotiService.verifyAge(payload.sessionId);
      this.logger.log(`Yoti verification result: ${JSON.stringify(result)}`);
    }

    return { received: true };
  }

  @Post('pipedrive/webhook')
  @UseGuards(ApiKeyGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Pipedrive CRM webhook' })
  @ApiResponse({ status: 200, description: 'Webhook processed' })
  async handlePipedriveWebhook(
    @Body() payload: { type: string; object: string; id: string; data: Record<string, unknown> },
  ): Promise<{ received: boolean }> {
    this.logger.log(`Pipedrive webhook: ${payload.type} - ${payload.id}`);

    if (payload.type === 'deal.update' && payload.data) {
      const dealData = payload.data as Record<string, unknown>;
      if (dealData['status'] === 'won') {
        this.logger.log(`Deal ${payload.id} marked as won`);
      }
    }

    return { received: true };
  }

  @Post('ccbill/webhook')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'CCBill payment webhook' })
  @ApiResponse({ status: 200, description: 'Webhook processed' })
  async handleCcbillWebhook(
    @Req() request: RawBodyRequest<Request>,
  ): Promise<{ received: boolean }> {
    const rawBody = request.rawBody?.toString() || '';

    this.logger.log(`CCBill webhook raw body: ${rawBody.substring(0, 500)}`);

    const payload = this.ccbillService.parseWebhookPayload(rawBody);

    if (!payload) {
      this.logger.warn('Failed to parse CCBill webhook payload');
      return { received: false };
    }

    this.logger.log(`CCBill webhook: type=${payload.type}, transactionId=${payload.transactionId}, status=${payload.status}`);

    if (payload.type === 'NewSubscription' && payload.subscriptionId) {
      this.logger.log(`New subscription: ${payload.subscriptionId}`);
    }

    if (payload.type === 'Renewal' && payload.subscriptionId) {
      this.logger.log(`Subscription renewed: ${payload.subscriptionId}`);
    }

    if (payload.type === 'Cancellation' && payload.subscriptionId) {
      this.logger.log(`Subscription cancelled: ${payload.subscriptionId}`);
      await this.ccbillService.cancelSubscription(payload.subscriptionId);
    }

    return { received: true };
  }

  @Post('yoti/sessions')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create Yoti verification session' })
  @ApiResponse({ status: 201, description: 'Session created' })
  async createYotiSession(
    @Body() body: { userId: string; phone: string },
  ): Promise<{ sessionId: string; shareUrl: string } | { error: string }> {
    const result = await this.yotiService.createSession(body.userId, body.phone);

    if (!result) {
      return { error: 'Failed to create session' };
    }

    return result;
  }

  @Post('ccbill/payment-link')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create CCBill payment link' })
  @ApiResponse({ status: 201, description: 'Payment link created' })
  async createPaymentLink(
    @Body()
    body: {
      amount: number;
      userId: string;
      email: string;
      firstName: string;
      lastName: string;
      description: string;
    },
  ): Promise<{ paymentUrl: string; transactionId: string } | { error: string }> {
    const result = await this.ccbillService.createPaymentLink(body);

    if (!result) {
      return { error: 'Failed to create payment link' };
    }

    return result;
  }

  @Post('health/integrations')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Check all integration services health' })
  @ApiResponse({ status: 200, description: 'Health status of all integrations' })
  async checkIntegrationsHealth(): Promise<{
    yoti: boolean;
    pipedrive: boolean;
    ccbill: boolean;
  }> {
    const [yotiHealth, pipedriveHealth, ccbillHealth] = await Promise.all([
      this.yotiService.testConnection(),
      this.pipedriveService.testConnection(),
      this.ccbillService.testConnection(),
    ]);

    return {
      yoti: yotiHealth,
      pipedrive: pipedriveHealth,
      ccbill: ccbillHealth,
    };
  }
}