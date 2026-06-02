import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import { ValidationPipe, Logger } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import * as winston from 'winston';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';
import { LoggingInterceptor } from './common/interceptors/logging.interceptor';
import { TransformInterceptor } from './common/interceptors/transform.interceptor';

// Winston logger configuration
const winstonLogger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json(),
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(({ level, message, timestamp, stack }) => {
          return `${timestamp} ${level}: ${stack || message}`;
        }),
      ),
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880,
      maxFiles: 5,
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880,
      maxFiles: 5,
    }),
  ],
});

async function bootstrap(): Promise<void> {
  const logger = new Logger('Bootstrap');

  const app = await NestFactory.create(AppModule, {
    logger: winstonLogger,
  });

  const configService = app.get(ConfigService);
  const port = configService.get<number>('PORT', 3000);
  const environment = configService.get<string>('NODE_ENV', 'development');

  // Global prefix for all routes
  app.setGlobalPrefix('api/v1', {
    exclude: ['health', 'api/docs'],
  });

  // Enable CORS
  app.enableCors({
    origin: configService.get<string[]>('CORS_ORIGINS', ['http://localhost:3000']),
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key'],
    credentials: true,
    maxAge: 86400,
  });

  // Security headers with Helmet
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
      },
    },
    crossOriginEmbedderPolicy: false,
  }));

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
      exceptionFactory: (errors) => {
        const formattedErrors = errors.map((error) => ({
          field: error.property,
          message: Object.values(error.constraints ?? {}).join(', '),
        }));
        return {
          statusCode: 400,
          message: 'Validation failed',
          errors: formattedErrors,
        };
      },
    }),
  );

  // Global exception filter
  app.useGlobalFilters(new HttpExceptionFilter());

  // Global interceptors
  app.useGlobalInterceptors(new LoggingInterceptor(), new TransformInterceptor());

  // Swagger documentation setup
  const swaggerConfig = new DocumentBuilder()
    .setTitle('Premium Service Directory API')
    .setDescription('API documentation for Premium Service Directory Platform')
    .setVersion('1.0')
    .addBearerAuth(
      {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        name: 'JWT',
        description: 'Enter JWT token',
        in: 'header',
      },
      'JWT-auth',
    )
    .addApiKey({ type: 'apiKey', name: 'X-API-Key', in: 'header' }, 'api-key')
    .addTag('auth', 'Authentication endpoints')
    .addTag('users', 'User management endpoints')
    .addTag('listings', 'Service listings endpoints')
    .addTag('payments', 'Payment processing endpoints')
    .addTag('integrations', 'Third-party integrations')
    .addTag('health', 'Health check endpoints')
    .build();

  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('api/docs', app, document, {
    swaggerOptions: {
      persistAuthorization: true,
      docExpansion: 'list',
      filter: true,
      showRequestDuration: true,
    },
    customSiteTitle: 'Premium Directory API Docs',
    customCss: '.swagger-ui .topbar { display: none }',
    customfavIcon: '/api/docs/favicon.ico',
  });

  // Enable shutdown hooks for graceful shutdown
  app.enableShutdownHooks();

  await app.listen(port);
  logger.log(`Application is running on: http://localhost:${port}/api/v1`);
  logger.log(`Environment: ${environment}`);
  logger.log(`Swagger documentation: http://localhost:${port}/api/docs`);
}

bootstrap().catch((error) => {
  const logger = new Logger('BootstrapError');
  logger.error(`Failed to start application: ${error.message}`, error.stack);
  process.exit(1);
});