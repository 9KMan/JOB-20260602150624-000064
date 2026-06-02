import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
} from 'typeorm';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
  CANCELLED = 'cancelled',
}

export enum PaymentMethod {
  CREDIT_CARD = 'credit_card',
  DEBIT_CARD = 'debit_card',
  ACH_TRANSFER = 'ach_transfer',
  PAYPAL = 'paypal',
  CCBILL = 'ccbill',
}

@Entity('payments')
@Index('idx_payments_user', ['userId'])
@Index('idx_payments_status', ['status'])
@Index('idx_payments_external_id', ['externalTransactionId'], { unique: true })
export class Payment {
  @ApiProperty({ description: 'Unique identifier (UUID)', format: 'uuid' })
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ApiProperty({ description: 'Associated user ID', format: 'uuid' })
  @Column({ type: 'uuid' })
  userId: string;

  @ApiPropertyOptional({ description: 'Associated listing ID (for listing purchases)', format: 'uuid' })
  @Column({ type: 'uuid', nullable: true })
  listingId: string | null;

  @ApiProperty({ example: 99.99, description: 'Payment amount' })
  @Column({ type: 'decimal', precision: 10, scale: 2 })
  amount: number;

  @ApiProperty({ example: 'USD', description: 'Currency code' })
  @Column({ type: 'varchar', length: 3 })
  currency: string;

  @ApiProperty({ enum: PaymentStatus, example: 'PENDING' })
  @Column({ type: 'varchar', length: 20, default: PaymentStatus.PENDING })
  status: PaymentStatus;

  @ApiProperty({ enum: PaymentMethod, example: 'CREDIT_CARD' })
  @Column({ type: 'varchar', length: 20 })
  method: PaymentMethod;

  @ApiPropertyOptional({ example: 'ch_1234567890', description: 'External transaction ID' })
  @Column({ type: 'varchar', length: 255, nullable: true, unique: true })
  externalTransactionId: string | null;

  @ApiPropertyOptional({ example: 'pi_1234567890', description: 'Payment intent ID' })
  @Column({ type: 'varchar', length: 255, nullable: true })
  paymentIntentId: string | null;

  @ApiPropertyOptional({ example: 'card_1234', description: 'Last 4 digits of card' })
  @Column({ type: 'varchar', length: 4, nullable: true })
  cardLast4: string | null;

  @ApiPropertyOptional({ example: 'visa', description: 'Card brand' })
  @Column({ type: 'varchar', length: 20, nullable: true })
  cardBrand: string | null;

  @ApiPropertyOptional({ description: 'Failure reason if payment failed' })
  @Column({ type: 'text', nullable: true })
  failureReason: string | null;

  @ApiPropertyOptional({ description: 'Metadata JSON' })
  @Column({ type: 'jsonb', nullable: true })
  metadata: Record<string, unknown> | null;

  @ApiProperty({ description: 'Creation timestamp' })
  @CreateDateColumn({ type: 'timestamp' })
  createdAt: Date;

  @ApiProperty({ description: 'Last update timestamp' })
  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt: Date;
}