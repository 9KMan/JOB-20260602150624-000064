import { Module, Global } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { configuration } from './configuration';
import { dataSourceOptions } from './typeorm.config';

@Global()
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
      envFilePath: ['.env.development', '.env.production', '.env'],
      expandVariables: true,
    }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => {
        const dbConfig = configService.get<{
          host: string;
          port: number;
          username: string;
          password: string;
          database: string;
          synchronize: boolean;
          logging: boolean;
        }>('database');

        return {
          type: 'postgres',
          host: dbConfig?.host || 'localhost',
          port: dbConfig?.port || 5432,
          username: dbConfig?.username || 'postgres',
          password: dbConfig?.password || 'postgres',
          database: dbConfig?.database || 'premium_directory',
          entities: [__dirname + '/../**/*.entity{.ts,.js}'],
          synchronize: dbConfig?.synchronize ?? false,
          logging: dbConfig?.logging ?? false,
          autoLoadEntities: true,
          ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
        } as any;
      },
    }),
  ],
  exports: [ConfigModule, TypeOrmModule],
})
export class AppConfigModule {}