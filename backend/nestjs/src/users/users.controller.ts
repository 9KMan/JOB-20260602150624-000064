import {
  Controller,
  Get,
  Post,
  Put,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  UseGuards,
  Logger,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiParam,
  ApiQuery,
} from '@nestjs/swagger';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../auth/roles.guard';
import { Roles } from '../auth/roles.decorator';
import { UserRole } from './entities/user.entity';

@ApiTags('users')
@Controller('users')
@UseGuards(JwtAuthGuard, RolesGuard)
@ApiBearerAuth('JWT-auth')
export class UsersController {
  private readonly logger = new Logger(UsersController.name);

  constructor(private readonly usersService: UsersService) {}

  @Post()
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Create a new user (admin only)' })
  @ApiResponse({ status: 201, description: 'User created successfully' })
  @ApiResponse({ status: 400, description: 'Validation error' })
  @ApiResponse({ status: 409, description: 'Email already exists' })
  async create(@Body() createUserDto: CreateUserDto) {
    this.logger.log('Creating new user');
    return this.usersService.create(createUserDto);
  }

  @Get()
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Get all users (admin only)' })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiQuery({ name: 'offset', required: false, type: Number })
  @ApiQuery({ name: 'role', required: false, enum: UserRole })
  @ApiResponse({ status: 200, description: 'List of users' })
  async findAll(
    @Query('limit') limit?: number,
    @Query('offset') offset?: number,
    @Query('role') role?: UserRole,
  ) {
    return this.usersService.findAll({ limit, offset, role });
  }

  @Get(':id')
  @Roles(UserRole.ADMIN, UserRole.MODERATOR)
  @ApiOperation({ summary: 'Get user by ID' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'User details' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async findOne(@Param('id') id: string) {
    return this.usersService.findByIdOrFail(id);
  }

  @Get('email/:email')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Get user by email' })
  @ApiParam({ name: 'email', format: 'email' })
  @ApiResponse({ status: 200, description: 'User details' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async findByEmail(@Param('email') email: string) {
    return this.usersService.findByEmailOrFail(email);
  }

  @Put(':id')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Update user (admin only)' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'User updated successfully' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async update(
    @Param('id') id: string,
    @Body() updateUserDto: UpdateUserDto,
  ) {
    this.logger.log(`Updating user: ${id}`);
    return this.usersService.update(id, updateUserDto);
  }

  @Patch(':id/password')
  @Roles(UserRole.ADMIN)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Update user password (admin only)' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Password updated successfully' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async updatePassword(
    @Param('id') id: string,
    @Body() body: { newPassword: string },
  ) {
    this.logger.log(`Updating password for user: ${id}`);
    await this.usersService.updatePassword(id, body.newPassword);
    return { message: 'Password updated successfully' };
  }

  @Delete(':id')
  @Roles(UserRole.ADMIN)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Soft delete user (admin only)' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'User deleted successfully' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async remove(@Param('id') id: string) {
    this.logger.log(`Soft deleting user: ${id}`);
    await this.usersService.softDelete(id);
    return { message: 'User deleted successfully' };
  }

  @Post(':id/restore')
  @Roles(UserRole.ADMIN)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Restore deleted user (admin only)' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'User restored successfully' })
  @ApiResponse({ status: 404, description: 'User not found' })
  async restore(@Param('id') id: string) {
    this.logger.log(`Restoring user: ${id}`);
    return this.usersService.restore(id);
  }
}