import { PartialType } from '@nestjs/swagger';
import { IsString, IsEmail, IsOptional, IsBoolean, IsPhoneNumber, IsArray, IsEnum } from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';
import { UserRole } from '../entities/user.entity';

export class UpdateUserDto {
  @ApiPropertyOptional({ example: 'Jane' })
  @IsOptional()
  @IsString()
  firstName?: string;

  @ApiPropertyOptional({ example: 'Smith' })
  @IsOptional()
  @IsString()
  lastName?: string;

  @ApiPropertyOptional({ example: '+1987654321' })
  @IsOptional()
  @IsPhoneNumber('US', { message: 'Please provide a valid US phone number' })
  phone?: string;

  @ApiPropertyOptional({ example: true })
  @IsOptional()
  @IsBoolean()
  marketingOptIn?: boolean;

  @ApiPropertyOptional({ example: ['user', 'admin'], enum: UserRole })
  @IsOptional()
  @IsArray()
  @IsEnum(UserRole, { each: true })
  roles?: UserRole[];

  @ApiPropertyOptional({ example: true })
  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}