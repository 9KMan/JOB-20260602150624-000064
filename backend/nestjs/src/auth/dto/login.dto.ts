import { IsString, IsEmail, IsNotEmpty, MinLength, MaxLength, IsOptional, IsEnum, IsUUID, IsDateString, IsBoolean, IsNumber, IsArray, IsUrl, IsPhoneNumber, IsMobilePhone } from 'class-validator';
import { ApiProperty, ApiPropertyOptional, PartialType } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { UserRole } from '../../users/entities/user.entity';

export class RegisterDto {
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

export class LoginDto {
  @ApiProperty({ example: 'john.doe@example.com', description: 'User email address' })
  @IsEmail({}, { message: 'Please provide a valid email address' })
  @IsNotEmpty({ message: 'Email is required' })
  @Transform(({ value }) => value?.toLowerCase().trim())
  email: string;

  @ApiProperty({ example: 'SecurePass123!', description: 'User password' })
  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  password: string;
}

export class RefreshTokenDto {
  @ApiProperty({ example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', description: 'Refresh token' })
  @IsString()
  @IsNotEmpty({ message: 'Refresh token is required' })
  refreshToken: string;
}

export class LogoutDto {
  @ApiPropertyOptional({ description: 'Refresh token to invalidate' })
  @IsOptional()
  @IsString()
  refreshToken?: string;
}