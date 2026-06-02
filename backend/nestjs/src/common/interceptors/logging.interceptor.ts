import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Request, Response } from 'express';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const ctx = context.switchToHttp();
    const request = ctx.getRequest<Request>();
    const response = ctx.getResponse<Response>();

    const { method, url, ip } = request;
    const userAgent = request.get('user-agent') || 'unknown';
    const startTime = Date.now();

    const contextId = context.getClass().name + '.' + context.getHandler().name;

    return next.handle().pipe(
      tap({
        next: () => {
          const statusCode = response.statusCode;
          const duration = Date.now() - startTime;
          const contentLength = response.get('content-length') || 0;

          this.logger.log(
            `${method} ${url} ${statusCode} - ${duration}ms - ${ip} - ${userAgent} - ${contentLength}b`,
          );
        },
        error: (error: Error) => {
          const duration = Date.now() - startTime;
          const statusCode = response.statusCode || 500;

          this.logger.error(
            `${method} ${url} ${statusCode} - ${duration}ms - ${ip} - ${error.message}`,
          );
        },
      }),
    );
  }
}