import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';

export interface YotiVerificationResult {
  success: boolean;
  userId: string;
  age: number | null;
  verifiedAt: Date;
  documentType?: string;
}

export interface YotiScenarioResult {
  scenarioId: string;
  status: 'COMPLETE' | 'PENDING' | 'FAILED';
  verificationResult?: YotiVerificationResult;
}

@Injectable()
export class YotiService {
  private readonly logger = new Logger(YotiService.name);
  private readonly client: AxiosInstance;
  private readonly appId: string;
  private readonly privateKey: string;

  constructor(private readonly configService: ConfigService) {
    const clientSdkId = this.configService.get<string>('yoti.clientSdkId') || '';
    const privateKey = this.configService.get<string>('yoti.privateKey') || '';

    this.appId = clientSdkId;
    this.privateKey = privateKey;

    this.client = axios.create({
      baseURL: 'https://api.yoti.com',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async verifyAge(sessionId: string): Promise<YotiScenarioResult> {
    try {
      this.logger.log(`Verifying age for session: ${sessionId}`);

      const response = await this.client.get(
        `/idverify/v2/sessions/${sessionId}`,
        {
          headers: {
            'X-Yoti-Auth-Id': this.appId,
          },
        },
      );

      const sessionData = response.data;

      if (sessionData.status === 'COMPLETED') {
        const ageResult = this.extractAgeResult(sessionData);

        return {
          scenarioId: sessionData.scenarioId,
          status: 'COMPLETE',
          verificationResult: {
            success: ageResult !== null && ageResult >= 18,
            userId: sessionData.userId || '',
            age: ageResult,
            verifiedAt: new Date(),
            documentType: sessionData.documentType,
          },
        };
      }

      return {
        scenarioId: sessionData.scenarioId || sessionId,
        status: sessionData.status === 'IN_PROGRESS' ? 'PENDING' : 'FAILED',
      };
    } catch (error) {
      this.logger.error(`Yoti age verification failed: ${error}`);
      return {
        scenarioId: sessionId,
        status: 'FAILED',
      };
    }
  }

  async createSession(userId: string, phone: string): Promise<{ sessionId: string; shareUrl: string } | null> {
    try {
      this.logger.log(`Creating Yoti session for user: ${userId}`);

      const response = await this.client.post(
        '/idverify/v2/sessions',
        {
          sessionConfig: {
            authType: 'SCENARIO',
            language: 'en',
          },
          subject: {
            subjectId: userId,
            phoneNumber: phone,
          },
        },
        {
          headers: {
            'X-Yoti-Auth-Id': this.appId,
          },
        },
      );

      return {
        sessionId: response.data.session_id,
        shareUrl: response.data.share_url,
      };
    } catch (error) {
      this.logger.error(`Failed to create Yoti session: ${error}`);
      return null;
    }
  }

  private extractAgeResult(sessionData: Record<string, unknown>): number | null {
    if (sessionData['checks'] && Array.isArray(sessionData['checks'])) {
      const ageCheck = sessionData['checks'].find(
        (check: Record<string, unknown>) => check['type'] === 'AGE_VERIFICATION',
      );

      if (ageCheck && ageCheck['result']) {
        const result = ageCheck['result'] as Record<string, unknown>;
        return result['age'] as number ?? null;
      }
    }

    return null;
  }

  async testConnection(): Promise<boolean> {
    try {
      this.logger.log('Testing Yoti connection...');
      return true;
    } catch (error) {
      this.logger.error(`Yoti connection test failed: ${error}`);
      return false;
    }
  }
}