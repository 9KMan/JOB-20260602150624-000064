import {
  Injectable,
  UnauthorizedException,
  BadRequestException,
  Logger,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { UsersService } from '../users/users.service';
import { LoginDto } from './dto/login.dto';
import { RegisterDto } from './dto/register.dto';
import { JwtPayload } from './jwt.strategy';
import { User } from '../users/entities/user.entity';

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresIn: string;
}

export interface AuthResponse {
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    roles: string[];
  };
  tokens: TokenPair;
}

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {}

  async validateUser(email: string, password: string): Promise<User | null> {
    try {
      const user = await this.usersService.findByEmail(email);

      if (!user) {
        this.logger.debug(`Login attempt for non-existent email: ${email}`);
        return null;
      }

      const isPasswordValid = await this.usersService.validatePassword(
        user.id,
        password,
      );

      if (!isPasswordValid) {
        this.logger.debug(`Invalid password for user: ${email}`);
        return null;
      }

      if (!user.isActive) {
        this.logger.warn(`Login attempt for disabled account: ${email}`);
        return null;
      }

      await this.usersService.updateLastLogin(user.id);

      return user;
    } catch (error) {
      this.logger.error(`Error validating user ${email}: ${error}`);
      return null;
    }
  }

  async login(loginDto: LoginDto): Promise<AuthResponse> {
    const { email, password } = loginDto;

    const user = await this.validateUser(email, password);

    if (!user) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const tokens = await this.generateTokens(user);

    this.logger.log(`User ${email} logged in successfully`);

    return {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        roles: user.roles as string[],
      },
      tokens,
    };
  }

  async register(registerDto: RegisterDto): Promise<AuthResponse> {
    const existingUser = await this.usersService.findByEmail(registerDto.email);

    if (existingUser) {
      throw new BadRequestException('Email already registered');
    }

    const user = await this.usersService.create({
      email: registerDto.email,
      password: registerDto.password,
      firstName: registerDto.firstName,
      lastName: registerDto.lastName,
      phone: registerDto.phone,
      marketingOptIn: registerDto.marketingOptIn ?? false,
      roles: registerDto.roles ?? ['user'],
    });

    const tokens = await this.generateTokens(user);

    this.logger.log(`New user registered: ${user.email}`);

    return {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        roles: user.roles as string[],
      },
      tokens,
    };
  }

  async refreshToken(refreshToken: string): Promise<TokenPair> {
    try {
      const payload = this.jwtService.verify<JwtPayload>(refreshToken, {
        secret: this.configService.get<string>('jwt.refreshSecret'),
      });

      const user = await this.usersService.findById(payload.sub);

      if (!user || !user.isActive) {
        throw new UnauthorizedException('Invalid refresh token');
      }

      const tokens = await this.generateTokens(user);

      this.logger.log(`Token refreshed for user: ${user.email}`);

      return tokens;
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      this.logger.warn(`Invalid refresh token: ${error}`);
      throw new UnauthorizedException('Invalid or expired refresh token');
    }
  }

  async logout(userId: string): Promise<void> {
    this.logger.log(`User ${userId} logged out`);
  }

  private async generateTokens(user: User): Promise<TokenPair> {
    const payload: JwtPayload = {
      sub: user.id,
      email: user.email,
      roles: user.roles as string[],
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 900,
    };

    const [accessToken, refreshToken] = await Promise.all([
      this.jwtService.signAsync(payload, {
        secret: this.configService.get<string>('jwt.secret'),
        expiresIn: '15m',
      }),
      this.jwtService.signAsync(
        { sub: user.id, type: 'refresh' },
        {
          secret: this.configService.get<string>('jwt.refreshSecret'),
          expiresIn: '7d',
        },
      ),
    ]);

    return {
      accessToken,
      refreshToken,
      expiresIn: '15m',
    };
  }
}