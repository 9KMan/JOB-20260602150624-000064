import { Module } from '@nestjs/common';
import { YotiService } from './yoti.service';
import { PipedriveService } from './pipedrive.service';
import { CcbillService } from './ccbill.service';
import { IntegrationsController } from './integrations.controller';

@Module({
  controllers: [IntegrationsController],
  providers: [YotiService, PipedriveService, CcbillService],
  exports: [YotiService, PipedriveService, CcbillService],
})
export class IntegrationsModule {}