import { DataSource, DataSourceOptions } from 'typeorm';
import { config } from 'dotenv';
import { existsSync } from 'fs';
import { join } from 'path';
import { Initialize1689000000000Up } from '../migrations/1689000000000-Initialize.up';

config();

const nodeEnv = process.env.NODE_ENV || 'development';

const migrationDir = join(__dirname, '..', 'migrations');

export const dataSourceOptions: DataSourceOptions = {
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT ?? '5432', 10),
  username: process.env.DB_USERNAME || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
  database: process.env.DB_DATABASE || 'premium_directory',
  entities: [join(__dirname, '..', '**', '*.entity{.ts,.js}')],
  migrations: [migrationDir + '/*.{ts,js}'],
  migrationsTableName: 'typeorm_migrations',
  synchronize: nodeEnv === 'development',
  logging: nodeEnv === 'development',
  ssl: nodeEnv === 'production' ? { rejectUnauthorized: false } : false,
  extra: {
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
  },
};

const dataSource = new DataSource(dataSourceOptions);

export default dataSource;