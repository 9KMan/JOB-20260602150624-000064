import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AppConfigModule } from './config/app-config.module';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { ListingsModule } from './listings/listings.module';
import { PaymentsModule } from './payments/payments.module';
import { IntegrationsModule } from './integrations/integrations.module';
import { HealthModule } from './health/health.module';
import configuration from './config/configuration';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
      expandVariables: true,
    }),
    AppConfigModule,
    AuthModule,
    UsersModule,
    ListingsModule,
    PaymentsModule,
    IntegrationsModule,
    HealthModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}