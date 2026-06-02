import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  OneToMany,
  JoinColumn,
  Index,
} from 'typeorm';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export enum ListingStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  ACTIVE = 'active',
  PAUSED = 'paused',
  SUSPENDED = 'suspended',
  DELETED = 'deleted',
}

export enum ListingCategory {
  PLUMBING = 'PLUMBING',
  ELECTRICAL = 'ELECTRICAL',
  HVAC = 'HVAC',
  CLEANING = 'CLEANING',
  LANDSCAPING = 'LANDSCAPING',
  CONSTRUCTION = 'CONSTRUCTION',
  AUTOMOTIVE = 'AUTOMOTIVE',
  HEALTHCARE = 'HEALTHCARE',
  LEGAL = 'LEGAL',
  ACCOUNTING = 'ACCOUNTING',
  REAL_ESTATE = 'REAL_ESTATE',
  HOME_IMPROVEMENT = 'HOME_IMPROVEMENT',
  PET_CARE = 'PET_CARE',
  EVENT_PLANNING = 'EVENT_PLANNING',
  EDUCATION = 'EDUCATION',
  FITNESS = 'FITNESS',
  BEAUTY = 'BEAUTY',
  TECHNOLOGY = 'TECHNOLOGY',
  OTHER = 'OTHER',
}

@Entity('listings')
@Index('idx_listings_title', ['title'])
@Index('idx_listings_category', ['category'])
@Index('idx_listings_status', ['status'])
@Index('idx_listings_owner', ['ownerId'])
export class Listing {
  @ApiProperty({ description: 'Unique identifier (UUID)', format: 'uuid' })
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ApiProperty({ example: 'Premium Plumbing Services', description: 'Listing title' })
  @Column({ type: 'varchar', length: 200 })
  title: string;

  @ApiProperty({ example: 'Professional plumbing services...', description: 'Listing description' })
  @Column({ type: 'text' })
  description: string;

  @ApiProperty({ enum: ListingCategory, example: 'PLUMBING' })
  @Column({ type: 'varchar', length: 50 })
  category: ListingCategory;

  @ApiProperty({ enum: ListingStatus, example: 'ACTIVE' })
  @Column({ type: 'varchar', length: 20, default: ListingStatus.DRAFT })
  status: ListingStatus;

  @ApiProperty({ example: 75.00, description: 'Hourly rate' })
  @Column({ type: 'decimal', precision: 10, scale: 2, default: 0 })
  price: number;

  @ApiProperty({ example: 'USD', description: 'Currency code' })
  @Column({ type: 'varchar', length: 3, default: 'USD' })
  currency: string;

  @ApiPropertyOptional({ example: '123 Main St, New York, NY', description: 'Location address' })
  @Column({ type: 'varchar', length: 500, nullable: true })
  location: string | null;

  @ApiPropertyOptional({ description: 'Latitude and longitude coordinates' })
  @Column({ type: 'jsonb', nullable: true })
  coordinates: { lat: number; lng: number } | null;

  @ApiPropertyOptional({ example: '+1234567890', description: 'Contact phone' })
  @Column({ type: 'varchar', length: 20, nullable: true })
  contactPhone: string | null;

  @ApiPropertyOptional({ example: 'contact@example.com', description: 'Contact email' })
  @Column({ type: 'varchar', length: 255, nullable: true })
  contactEmail: string | null;

  @ApiPropertyOptional({ example: ['24/7 Service', 'Emergency Repairs'] })
  @Column({ type: 'simple-array', nullable: true })
  tags: string[] | null;

  @ApiProperty({ description: 'Owner user ID', format: 'uuid' })
  @Column({ type: 'uuid' })
  ownerId: string;

  @ApiPropertyOptional({ description: 'Yoti age verification status' })
  @Column({ type: 'boolean', default: false })
  ageVerified: boolean;

  @ApiPropertyOptional({ description: 'Listing view count' })
  @Column({ type: 'integer', default: 0 })
  viewCount: number;

  @ApiPropertyOptional({ description: 'Listing featured status' })
  @Column({ type: 'boolean', default: false })
  isFeatured: boolean;

  @ApiProperty({ description: 'Creation timestamp' })
  @CreateDateColumn({ type: 'timestamp' })
  createdAt: Date;

  @ApiProperty({ description: 'Last update timestamp' })
  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt: Date;
}

@Entity('categories')
@Index('idx_categories_name', ['name'], { unique: true })
export class Category {
  @ApiProperty({ description: 'Unique identifier (UUID)', format: 'uuid' })
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ApiProperty({ example: 'PLUMBING', description: 'Category code' })
  @Column({ type: 'varchar', length: 50, unique: true })
  code: string;

  @ApiProperty({ example: 'Plumbing Services', description: 'Category name' })
  @Column({ type: 'varchar', length: 100 })
  name: string;

  @ApiPropertyOptional({ example: 'Professional plumbing services for residential and commercial properties' })
  @Column({ type: 'text', nullable: true })
  description: string | null;

  @ApiPropertyOptional({ example: 'plumbing-icon.png' })
  @Column({ type: 'varchar', length: 255, nullable: true })
  iconUrl: string | null;

  @ApiPropertyOptional({ example: 1 })
  @Column({ type: 'integer', default: 0 })
  displayOrder: number;

  @ApiProperty({ example: true })
  @Column({ type: 'boolean', default: true })
  isActive: boolean;

  @ApiProperty({ description: 'Creation timestamp' })
  @CreateDateColumn({ type: 'timestamp' })
  createdAt: Date;

  @ApiProperty({ description: 'Last update timestamp' })
  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt: Date;
}

@Entity('listing_images')
@Index('idx_listing_images_listing', ['listingId'])
export class ListingImage {
  @ApiProperty({ description: 'Unique identifier (UUID)', format: 'uuid' })
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @ApiProperty({ description: 'Associated listing ID', format: 'uuid' })
  @Column({ type: 'uuid' })
  listingId: string;

  @ApiProperty({ example: 'https://example.com/image.jpg', description: 'Image URL' })
  @Column({ type: 'varchar', length: 500 })
  url: string;

  @ApiPropertyOptional({ example: 'Main listing image' })
  @Column({ type: 'varchar', length: 255, nullable: true })
  altText: string | null;

  @ApiPropertyOptional({ example: 1 })
  @Column({ type: 'integer', default: 0 })
  displayOrder: number;

  @ApiPropertyOptional({ example: 1024 })
  @Column({ type: 'integer', nullable: true })
  width: number | null;

  @ApiPropertyOptional({ example: 768 })
  @Column({ type: 'integer', nullable: true })
  height: number | null;

  @ApiPropertyOptional({ example: true })
  @Column({ type: 'boolean', default: true })
  isPrimary: boolean;

  @ApiProperty({ description: 'Creation timestamp' })
  @CreateDateColumn({ type: 'timestamp' })
  createdAt: Date;
}