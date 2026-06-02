import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { ApiProperty } from '@nestjs/swagger';

interface ErrorResponse {
  statusCode: number;
  message: string;
  error: string;
  timestamp: string;
  path: string;
  method: string;
  errors?: Array<{ field: string; message: string }>;
}

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let status: number;
    let message: string;
    let error: string;
    let errors: Array<{ field: string; message: string }> | undefined;

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === 'object' && exceptionResponse !== null) {
        const responseObj = exceptionResponse as Record<string, unknown>;
        message = (responseObj['message'] as string) || exception.message;
        error = (responseObj['error'] as string) || 'Error';

        if (Array.isArray(responseObj['errors'])) {
          errors = responseObj['errors'] as Array<{ field: string; message: string }>;
        } else if (typeof responseObj['message'] === 'object' && Array.isArray(responseObj['message'])) {
          errors = responseObj['message'] as Array<{ field: string; message: string }>;
        }
      } else {
        message = exception.message;
        error = 'Error';
      }
    } else if (exception instanceof Error) {
      status = HttpStatus.INTERNAL_SERVER_ERROR;
      message = exception.message || 'Internal server error';
      error = 'Internal Server Error';

      this.logger.error(
        `Unhandled exception: ${exception.message}`,
        exception.stack,
      );
    } else {
      status = HttpStatus.INTERNAL_SERVER_ERROR;
      message = 'An unexpected error occurred';
      error = 'Internal Server Error';

      this.logger.error(`Unknown exception type: ${JSON.stringify(exception)}`);
    }

    const errorResponse: ErrorResponse = {
      statusCode: status,
      message: message,
      error: error,
      timestamp: new Date().toISOString(),
      path: request.url,
      method: request.method,
    };

    if (errors) {
      errorResponse['errors'] = errors;
    }

    if (status === HttpStatus.INTERNAL_SERVER_ERROR) {
      this.logger.error(
        `${request.method} ${request.url} - ${status} - ${JSON.stringify(errorResponse)}`,
      );
    } else {
      this.logger.warn(
        `${request.method} ${request.url} - ${status} - ${message}`,
      );
    }

    response.status(status).json(errorResponse);
  }
}