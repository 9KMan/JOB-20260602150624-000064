import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
  Logger,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like, In, Between, LessThanOrEqual, MoreThanOrEqual } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { User, UserRole } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Injectable()
export class UsersService {
  private readonly logger = new Logger(UsersService.name);
  private readonly BCRYPT_ROUNDS = 12;

  constructor(
    @InjectRepository(User)
    private readonly usersRepository: Repository<User>,
  ) {}

  async create(createUserDto: CreateUserDto): Promise<User> {
    const existingUser = await this.findByEmail(createUserDto.email);

    if (existingUser) {
      throw new ConflictException('Email already exists');
    }

    const hashedPassword = await this.hashPassword(createUserDto.password);

    const user = this.usersRepository.create({
      email: createUserDto.email.toLowerCase().trim(),
      password: hashedPassword,
      firstName: createUserDto.firstName.trim(),
      lastName: createUserDto.lastName.trim(),
      phone: createUserDto.phone?.trim() || null,
      marketingOptIn: createUserDto.marketingOptIn ?? false,
      roles: createUserDto.roles ?? [UserRole.USER],
      isActive: true,
    });

    const savedUser = await this.usersRepository.save(user);

    this.logger.log(`User created: ${savedUser.email} (${savedUser.id})`);

    return savedUser;
  }

  async findAll(options?: {
    limit?: number;
    offset?: number;
    role?: UserRole;
    isActive?: boolean;
  }): Promise<{ users: User[]; total: number }> {
    const { limit = 20, offset = 0, role, isActive } = options ?? {};

    const queryBuilder = this.usersRepository
      .createQueryBuilder('user')
      .select(['user.id', 'user.email', 'user.firstName', 'user.lastName', 'user.roles', 'user.isActive', 'user.createdAt']);

    if (role) {
      queryBuilder.andWhere('user.roles LIKE :role', { role: `%${role}%` });
    }

    if (isActive !== undefined) {
      queryBuilder.andWhere('user.isActive = :isActive', { isActive });
    }

    const [users, total] = await queryBuilder
      .orderBy('user.createdAt', 'DESC')
      .skip(offset)
      .take(limit)
      .getManyAndCount();

    return { users, total };
  }

  async findById(id: string): Promise<User | null> {
    if (!id) {
      return null;
    }

    return this.usersRepository.findOne({
      where: { id },
      select: ['id', 'email', 'firstName', 'lastName', 'phone', 'roles', 'marketingOptIn', 'isActive', 'emailVerifiedAt', 'lastLoginAt', 'createdAt'],
    });
  }

  async findByIdOrFail(id: string): Promise<User> {
    const user = await this.findById(id);

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    return user;
  }

  async findByEmail(email: string): Promise<User | null> {
    if (!email) {
      return null;
    }

    return this.usersRepository.findOne({
      where: { email: email.toLowerCase().trim() },
    });
  }

  async findByEmailOrFail(email: string): Promise<User> {
    const user = await this.findByEmail(email);

    if (!user) {
      throw new NotFoundException(`User with email ${email} not found`);
    }

    return user;
  }

  async findByIds(ids: string[]): Promise<User[]> {
    return this.usersRepository.find({
      where: { id: In(ids) },
    });
  }

  async update(id: string, updateUserDto: UpdateUserDto): Promise<User> {
    const user = await this.findByIdOrFail(id);

    const updateData: Partial<User> = {};

    if (updateUserDto.firstName !== undefined) {
      updateData.firstName = updateUserDto.firstName.trim();
    }

    if (updateUserDto.lastName !== undefined) {
      updateData.lastName = updateUserDto.lastName.trim();
    }

    if (updateUserDto.phone !== undefined) {
      updateData.phone = updateUserDto.phone?.trim() || null;
    }

    if (updateUserDto.marketingOptIn !== undefined) {
      updateData.marketingOptIn = updateUserDto.marketingOptIn;
    }

    if (updateUserDto.roles !== undefined) {
      updateData.roles = updateUserDto.roles;
    }

    if (updateUserDto.isActive !== undefined) {
      updateData.isActive = updateUserDto.isActive;
    }

    Object.assign(user, updateData);

    return this.usersRepository.save(user);
  }

  async updatePassword(id: string, newPassword: string): Promise<void> {
    const user = await this.findByIdOrFail(id);

    const hashedPassword = await this.hashPassword(newPassword);

    user.password = hashedPassword;

    await this.usersRepository.save(user);

    this.logger.log(`Password updated for user: ${user.email}`);
  }

  async validatePassword(id: string, password: string): Promise<boolean> {
    const user = await this.usersRepository.findOne({
      where: { id },
      select: ['id', 'password'],
    });

    if (!user) {
      return false;
    }

    return bcrypt.compare(password, user.password);
  }

  async updateLastLogin(id: string): Promise<void> {
    await this.usersRepository.update(id, {
      lastLoginAt: new Date(),
    });
  }

  async softDelete(id: string): Promise<void> {
    const user = await this.findByIdOrFail(id);

    await this.usersRepository.softRemove(user);

    this.logger.log(`User soft deleted: ${user.email}`);
  }

  async restore(id: string): Promise<User> {
    const user = await this.usersRepository.findOne({
      where: { id },
      withDeleted: true,
    });

    if (!user || !user.deletedAt) {
      throw new NotFoundException(`User with ID ${id} not found or not deleted`);
    }

    await this.usersRepository.restore(id);

    return this.findByIdOrFail(id);
  }

  async exists(id: string): Promise<boolean> {
    const count = await this.usersRepository.count({
      where: { id },
    });
    return count > 0;
  }

  private async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, this.BCRYPT_ROUNDS);
  }
}