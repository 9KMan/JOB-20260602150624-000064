import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  Logger,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Request } from 'express';

@Injectable()
export class ApiKeyGuard implements CanActivate {
  private readonly logger = new Logger(ApiKeyGuard.name);
  private readonly validApiKey: string;

  constructor(private readonly configService: ConfigService) {
    this.validApiKey = this.configService.get<string>('api.key') || '';
  }

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest<Request>();
    const apiKey = request.get('X-API-Key');

    if (!apiKey) {
      this.logger.warn('API key header missing');
      throw new UnauthorizedException('API key is required');
    }

    if (!this.validApiKey) {
      this.logger.warn('API key not configured in environment');
      return true;
    }

    if (apiKey !== this.validApiKey) {
      this.logger.warn(`Invalid API key attempted: ${apiKey.substring(0, 8)}...`);
      throw new UnauthorizedException('Invalid API key');
    }

    return true;
  }
}