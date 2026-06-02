import { TypeOrmModuleOptions } from '@nestjs/typeorm';

export const configuration = (): Record<string, unknown> => ({
  nodeEnv: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT ?? '3000', 10),

  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT ?? '5432', 10),
    username: process.env.DB_USERNAME || 'postgres',
    password: process.env.DB_PASSWORD || 'postgres',
    database: process.env.DB_DATABASE || 'premium_directory',
    synchronize: process.env.NODE_ENV === 'development',
    logging: process.env.NODE_ENV === 'development',
  },

  jwt: {
    secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key',
    refreshSecret: process.env.JWT_REFRESH_SECRET || 'your-refresh-secret-key',
    expiresIn: '15m',
    refreshExpiresIn: '7d',
  },

  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT ?? '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined,
    db: parseInt(process.env.REDIS_DB ?? '0', 10),
  },

  yoti: {
    appId: process.env.YOTI_APP_ID || '',
    clientSdkId: process.env.YOTI_CLIENT_SDK_ID || '',
    privateKey: process.env.YOTI_PRIVATE_KEY || '',
  },

  pipedrive: {
    apiToken: process.env.PIPEDRIVE_API_TOKEN || '',
    companyDomain: process.env.PIPEDRIVE_COMPANY_DOMAIN || '',
  },

  ccbill: {
    accNum: process.env.CCBILL_ACC_NUM || '',
    subaccNum: process.env.CCBILL_SUBACC_NUM || '',
    securityKey: process.env.CCBILL_SECURITY_KEY || '',
    flexId: process.env.CCBILL_FLEX_ID || '',
    salt: process.env.CCBILL_SALT || '',
  },

  api: {
    key: process.env.API_KEY || '',
  },

  cors: {
    origins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  },

  swagger: {
    enabled: process.env.SWAGGER_ENABLED !== 'false',
    title: 'Premium Service Directory API',
    description: 'API documentation for Premium Service Directory Platform',
    version: '1.0',
    path: 'api/docs',
  },

  rateLimit: {
    ttl: parseInt(process.env.RATE_LIMIT_TTL ?? '60', 10),
    limit: parseInt(process.env.RATE_LIMIT_LIMIT ?? '100', 10),
  },

  log: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'json',
  },
});

export default configuration;