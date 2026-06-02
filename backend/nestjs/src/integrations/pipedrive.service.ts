import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';

export interface PipedrivePerson {
  id: string;
  name: string;
  email: string;
  phone: string;
}

export interface PipedriveDeal {
  id: string;
  title: string;
  status: string;
  value: number;
  currency: string;
}

export interface PipedriveActivity {
  id: string;
  subject: string;
  type: string;
  due_date: string;
  done: boolean;
}

@Injectable()
export class PipedriveService {
  private readonly logger = new Logger(PipedriveService.name);
  private readonly client: AxiosInstance;
  private readonly apiToken: string;
  private readonly companyDomain: string;

  constructor(private readonly configService: ConfigService) {
    const apiToken = this.configService.get<string>('pipedrive.apiToken') || '';
    const companyDomain = this.configService.get<string>('pipedrive.companyDomain') || '';

    this.apiToken = apiToken;
    this.companyDomain = companyDomain;

    this.client = axios.create({
      baseURL: `https://${companyDomain}.pipedrive.com/api/v1`,
      timeout: 30000,
      params: {
        api_token: apiToken,
      },
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async createPerson(data: {
    name: string;
    email: string;
    phone?: string;
    orgId?: string;
  }): Promise<PipedrivePerson | null> {
    try {
      this.logger.log(`Creating Pipedrive person: ${data.email}`);

      const response = await this.client.post('/persons', {
        name: data.name,
        email: data.email,
        phone: data.phone,
        org_id: data.orgId,
      });

      return response.data.data;
    } catch (error) {
      this.logger.error(`Failed to create Pipedrive person: ${error}`);
      return null;
    }
  }

  async findPersonByEmail(email: string): Promise<PipedrivePerson | null> {
    try {
      this.logger.log(`Finding Pipedrive person by email: ${email}`);

      const response = await this.client.get('/persons', {
        params: {
          search_term: email,
          search_by: 'email',
        },
      });

      const persons = response.data.data;
      return persons && persons.length > 0 ? persons[0] : null;
    } catch (error) {
      this.logger.error(`Failed to find Pipedrive person: ${error}`);
      return null;
    }
  }

  async createDeal(data: {
    title: string;
    personId: string;
    value: number;
    currency?: string;
    stageId?: string;
  }): Promise<PipedriveDeal | null> {
    try {
      this.logger.log(`Creating Pipedrive deal: ${data.title}`);

      const response = await this.client.post('/deals', {
        title: data.title,
        person_id: data.personId,
        value: data.value,
        currency: data.currency || 'USD',
        stage_id: data.stageId,
      });

      return response.data.data;
    } catch (error) {
      this.logger.error(`Failed to create Pipedrive deal: ${error}`);
      return null;
    }
  }

  async createActivity(data: {
    subject: string;
    type: string;
    dueDate: string;
    personId?: string;
    dealId?: string;
  }): Promise<PipedriveActivity | null> {
    try {
      this.logger.log(`Creating Pipedrive activity: ${data.subject}`);

      const response = await this.client.post('/activities', {
        subject: data.subject,
        type: data.type,
        due_date: data.dueDate,
        person_id: data.personId,
        deal_id: data.dealId,
      });

      return response.data.data;
    } catch (error) {
      this.logger.error(`Failed to create Pipedrive activity: ${error}`);
      return null;
    }
  }

  async updateDealStatus(dealId: string, status: 'won' | 'lost'): Promise<boolean> {
    try {
      this.logger.log(`Updating Pipedrive deal ${dealId} to ${status}`);

      await this.client.put(`/deals/${dealId}`, {
        status: status,
      });

      return true;
    } catch (error) {
      this.logger.error(`Failed to update Pipedrive deal: ${error}`);
      return false;
    }
  }

  async addNoteToDeal(dealId: string, content: string): Promise<boolean> {
    try {
      this.logger.log(`Adding note to Pipedrive deal: ${dealId}`);

      await this.client.post('/notes', {
        content: content,
        deal_id: dealId,
      });

      return true;
    } catch (error) {
      this.logger.error(`Failed to add note to Pipedrive deal: ${error}`);
      return false;
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      this.logger.log('Testing Pipedrive connection...');

      const response = await this.client.get('/users');

      return response.status === 200;
    } catch (error) {
      this.logger.error(`Pipedrive connection test failed: ${error}`);
      return false;
    }
  }
}