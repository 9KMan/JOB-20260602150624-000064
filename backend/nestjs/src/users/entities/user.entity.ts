import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  DeleteDateColumn,
  OneToMany,
  Index,
} from 'typeorm';
import { Exclude } from 'class-transformer';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum UserRole {
  USER = 'user',
  ADMIN = 'admin',
  MODERATOR = 'moderator',
  SERVICE_PROVIDER = 'service_provider',
}

@Entity('users')
@Index('idx_users_email', ['email'], { unique: true })
@Index('idx_users_deleted_at', ['deletedAt'])
export class User {
  @ApiProperty({ description: 'Unique identifier (UUID)', format: 'uuid' })
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ApiProperty({ example: 'john.doe@example.com', description: 'User email address' })
  @Column({ type: 'varchar', length: 255, unique: true })
  email: string;

  @ApiProperty({ description: 'User password (hashed)' })
  @Column({ type: 'varchar', length: 255 })
  @Exclude()
  password: string;

  @ApiProperty({ example: 'John', description: 'User first name' })
  @Column({ type: 'varchar', length: 100 })
  firstName: string;

  @ApiProperty({ example: 'Doe', description: 'User last name' })
  @Column({ type: 'varchar', length: 100 })
  lastName: string;

  @ApiPropertyOptional({ example: '+1234567890', description: 'User phone number' })
  @Column({ type: 'varchar', length: 20, nullable: true })
  phone: string | null;

  @ApiProperty({ example: ['user'], description: 'User roles' })
  @Column({ type: 'simple-array', default: UserRole.USER })
  roles: UserRole[];

  @ApiProperty({ example: true, description: 'Marketing opt-in status' })
  @Column({ type: 'boolean', default: false })
  marketingOptIn: boolean;

  @ApiProperty({ example: true, description: 'Account active status' })
  @Column({ type: 'boolean', default: true })
  isActive: boolean;

  @ApiPropertyOptional({ description: 'Email verification timestamp' })
  @Column({ type: 'timestamp', nullable: true })
  emailVerifiedAt: Date | null;

  @ApiPropertyOptional({ description: 'Last login timestamp' })
  @Column({ type: 'timestamp', nullable: true })
  lastLoginAt: Date | null;

  @ApiProperty({ description: 'Account creation timestamp' })
  @CreateDateColumn({ type: 'timestamp' })
  createdAt: Date;

  @ApiProperty({ description: 'Account last update timestamp' })
  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt: Date;

  @ApiPropertyOptional({ description: 'Soft delete timestamp' })
  @DeleteDateColumn({ type: 'timestamp', nullable: true })
  deletedAt: Date | null;

  fullName(): string {
    return `${this.firstName} ${this.lastName}`;
  }
}