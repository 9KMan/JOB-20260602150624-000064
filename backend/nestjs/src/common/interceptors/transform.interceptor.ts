import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiProperty } from '@nestjs/swagger';

export interface ApiResponse<T> {
  @ApiProperty()
  success: boolean;
  @ApiProperty()
  data: T;
  @ApiProperty()
  timestamp: string;
  @ApiPropertyOptional()
  message?: string;
  @ApiPropertyOptional()
  meta?: Record<string, unknown>;
}

@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, ApiResponse<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map((data) => {
        const response: ApiResponse<T> = {
          success: true,
          data: data as T,
          timestamp: new Date().toISOString(),
        };

        if (data && typeof data === 'object' && 'message' in data) {
          response['message'] = (data as Record<string, unknown>)['message'] as string;
        }

        if (data && typeof data === 'object' && 'meta' in data) {
          response['meta'] = (data as Record<string, unknown>)['meta'] as Record<string, unknown>;
        }

        return response;
      }),
    );
  }
}