import { Controller, Get, Logger } from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
} from '@nestjs/swagger';
import {
  HealthCheck,
  HealthCheckService,
  TypeOrmHealthIndicator,
  HealthCheckResult,
} from '@nestjs/terminus';
import { RedisHealthIndicator } from './redis.health';

@ApiTags('health')
@Controller('health')
export class HealthController {
  private readonly logger = new Logger(HealthController.name);

  constructor(
    private readonly health: HealthCheckService,
    private readonly db: TypeOrmHealthIndicator,
    private readonly redis: RedisHealthIndicator,
  ) {}

  @Get()
  @HealthCheck()
  @ApiOperation({ summary: 'Health check endpoint for ALB' })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  @ApiResponse({ status: 503, description: 'Service is unhealthy' })
  async check(): Promise<HealthCheckResult> {
    this.logger.debug('Health check requested');

    return this.health.check([
      () => this.db.pingCheck('database'),
      () => this.redis.isHealthy('redis'),
    ]);
  }

  @Get('ping')
  @ApiOperation({ summary: 'Simple ping endpoint' })
  @ApiResponse({ status: 200, description: 'Pong' })
  async ping(): Promise<{ status: string; timestamp: string }> {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
    };
  }

  @Get('ready')
  @HealthCheck()
  @ApiOperation({ summary: 'Readiness probe for ALB' })
  @ApiResponse({ status: 200, description: 'Service is ready' })
  @ApiResponse({ status: 503, description: 'Service is not ready' })
  async ready(): Promise<HealthCheckResult> {
    return this.health.check([
      () => this.db.pingCheck('database'),
    ]);
  }

  @Get('live')
  @ApiOperation({ summary: 'Liveness probe for container restarts' })
  @ApiResponse({ status: 200, description: 'Service is alive' })
  async live(): Promise<{ status: string }> {
    return { status: 'ok' };
  }
}