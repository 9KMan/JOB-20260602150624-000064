import { IsString, IsNotEmpty, MinLength, MaxLength, IsOptional, IsEnum, IsNumber, IsUUID, IsDateString, IsArray, IsUrl, Min, Max } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import { ListingStatus, ListingCategory } from '../entities/listing.entity';

export class CreateListingDto {
  @ApiProperty({ example: 'Premium Plumbing Services', description: 'Listing title' })
  @IsString()
  @IsNotEmpty({ message: 'Title is required' })
  @MinLength(3, { message: 'Title must be at least 3 characters' })
  @MaxLength(200, { message: 'Title must not exceed 200 characters' })
  title: string;

  @ApiProperty({ example: 'Professional plumbing services for residential and commercial properties...', description: 'Listing description' })
  @IsString()
  @IsNotEmpty({ message: 'Description is required' })
  @MinLength(10, { message: 'Description must be at least 10 characters' })
  @MaxLength(5000, { message: 'Description must not exceed 5000 characters' })
  description: string;

  @ApiProperty({ example: 'PLUMBING', enum: ListingCategory, description: 'Listing category' })
  @IsEnum(ListingCategory, { message: 'Invalid category' })
  category: ListingCategory;

  @ApiProperty({ example: 75.00, description: 'Hourly rate' })
  @IsNumber()
  @Min(0, { message: 'Price must be at least 0' })
  @Max(100000, { message: 'Price must not exceed 100000' })
  price: number;

  @ApiProperty({ example: 'USD', description: 'Currency code' })
  @IsString()
  @IsNotEmpty()
  currency: string;

  @ApiPropertyOptional({ example: 'https://example.com/image.jpg' })
  @IsOptional()
  @IsArray()
  @IsUrl({}, { each: true })
  images?: string[];

  @ApiPropertyOptional({ example: { street: '123 Main St', city: 'New York', state: 'NY', zipCode: '10001', country: 'USA' } })
  @IsOptional()
  @IsString()
  location?: string;

  @ApiPropertyOptional({ example: { lat: 40.7128, lng: -74.0060 } })
  @IsOptional()
  coordinates?: { lat: number; lng: number };

  @ApiPropertyOptional({ example: '+1234567890' })
  @IsOptional()
  @IsString()
  contactPhone?: string;

  @ApiPropertyOptional({ example: 'contact@example.com' })
  @IsOptional()
  @IsString()
  contactEmail?: string;

  @ApiPropertyOptional({ example: ['24/7 Service', 'Emergency Repairs'] })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];
}

export class UpdateListingDto {
  @ApiPropertyOptional({ example: 'Premium Plumbing Services - Updated' })
  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(200)
  title?: string;

  @ApiPropertyOptional({ example: 'Updated description...' })
  @IsOptional()
  @IsString()
  @MinLength(10)
  @MaxLength(5000)
  description?: string;

  @ApiPropertyOptional({ enum: ListingCategory })
  @IsOptional()
  @IsEnum(ListingCategory)
  category?: ListingCategory;

  @ApiPropertyOptional({ example: 85.00 })
  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100000)
  price?: number;

  @ApiPropertyOptional({ example: 'USD' })
  @IsOptional()
  @IsString()
  currency?: string;

  @ApiPropertyOptional({ example: 'ACTIVE', enum: ListingStatus })
  @IsOptional()
  @IsEnum(ListingStatus)
  status?: ListingStatus;

  @ApiPropertyOptional()
  @IsOptional()
  @IsArray()
  @IsUrl({}, { each: true })
  images?: string[];

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  location?: string;

  @ApiPropertyOptional()
  @IsOptional()
  coordinates?: { lat: number; lng: number };

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  contactPhone?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  contactEmail?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];
}

export class SearchListingsDto {
  @ApiPropertyOptional({ example: 'plumbing' })
  @IsOptional()
  @IsString()
  @Transform(({ value }) => value?.trim())
  query?: string;

  @ApiPropertyOptional({ enum: ListingCategory })
  @IsOptional()
  @IsEnum(ListingCategory)
  category?: ListingCategory;

  @ApiPropertyOptional({ enum: ListingStatus })
  @IsOptional()
  @IsEnum(ListingStatus)
  status?: ListingStatus;

  @ApiPropertyOptional({ example: 0 })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(0)
  minPrice?: number;

  @ApiPropertyOptional({ example: 1000 })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Max(100000)
  maxPrice?: number;

  @ApiPropertyOptional({ example: 'New York' })
  @IsOptional()
  @IsString()
  location?: string;

  @ApiPropertyOptional({ example: 10 })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(100)
  limit?: number;

  @ApiPropertyOptional({ example: 0 })
  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(0)
  offset?: number;

  @ApiPropertyOptional({ example: 'createdAt' })
  @IsOptional()
  @IsString()
  sortBy?: string;

  @ApiPropertyOptional({ example: 'DESC' })
  @IsOptional()
  @IsEnum(['ASC', 'DESC'])
  sortOrder?: 'ASC' | 'DESC';
}