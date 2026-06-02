import { Injectable } from '@nestjs/terminus';
import { HealthIndicator, HealthIndicatorResult, HealthCheckError } from '@nestjs/terminus';
import { ConfigService } from '@nestjs/config';
import Redis from 'ioredis';

@Injectable()
export class RedisHealthIndicator extends HealthIndicator {
  private readonly logger = require('winston').createLogger({ silent: true });

  constructor(private readonly configService: ConfigService) {
    super();
  }

  async isHealthy(key: string): Promise<HealthIndicatorResult> {
    try {
      const redisConfig = {
        host: this.configService.get<string>('redis.host') || 'localhost',
        port: this.configService.get<number>('redis.port') || 6379,
        password: this.configService.get<string>('redis.password') || undefined,
        db: this.configService.get<number>('redis.db') || 0,
        retryStrategy: (times: number) => null,
        maxRetriesPerRequest: 1,
      };

      const redis = new Redis(redisConfig);

      const result = await redis.ping();

      await redis.quit();

      if (result === 'PONG') {
        return this.getStatus(key, true);
      }

      throw new HealthCheckError(
        'Redis health check failed',
        this.getStatus(key, false, { message: 'Ping failed' }),
      );
    } catch (error) {
      throw new HealthCheckError(
        'Redis health check failed',
        this.getStatus(key, false, { message: error instanceof Error ? error.message : 'Unknown error' }),
      );
    }
  }
}