import { IsString, IsEmail, IsNotEmpty, MinLength, MaxLength, IsOptional, IsEnum, IsUUID, IsDateString, IsBoolean, IsNumber, IsArray, IsUrl, IsPhoneNumber } from 'class-validator';
import { ApiProperty, ApiPropertyOptional, PartialType } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { UserRole } from '../../users/entities/user.entity';

export class CreateUserDto {
  @ApiProperty({ example: 'john.doe@example.com', description: 'User email address' })
  @IsEmail({}, { message: 'Please provide a valid email address' })
  @IsNotEmpty({ message: 'Email is required' })
  @Transform(({ value }) => value?.toLowerCase().trim())
  email: string;

  @ApiProperty({ example: 'SecurePass123!', description: 'User password (min 8 chars)' })
  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  @MinLength(8, { message: 'Password must be at least 8 characters long' })
  @MaxLength(128, { message: 'Password must not exceed 128 characters' })
  password: string;

  @ApiProperty({ example: 'John', description: 'User first name' })
  @IsString()
  @IsNotEmpty({ message: 'First name is required' })
  @MinLength(1)
  @MaxLength(100)
  firstName: string;

  @ApiProperty({ example: 'Doe', description: 'User last name' })
  @IsString()
  @IsNotEmpty({ message: 'Last name is required' })
  @MinLength(1)
  @MaxLength(100)
  lastName: string;

  @ApiPropertyOptional({ example: '+1234567890', description: 'User phone number' })
  @IsOptional()
  @IsPhoneNumber('US', { message: 'Please provide a valid US phone number' })
  phone?: string;

  @ApiPropertyOptional({ example: true, description: 'Marketing opt-in' })
  @IsOptional()
  @IsBoolean()
  marketingOptIn?: boolean;

  @ApiPropertyOptional({ example: ['user'], description: 'User roles', enum: UserRole })
  @IsOptional()
  @IsArray()
  @IsEnum(UserRole, { each: true })
  roles?: UserRole[];
}