import { Injectable, UnauthorizedException, Logger } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { UsersService } from '../../users/users.service';

export interface JwtPayload {
  sub: string;
  email: string;
  roles: string[];
  iat: number;
  exp: number;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, 'jwt') {
  private readonly logger = new Logger(JwtStrategy.name);

  constructor(
    private readonly configService: ConfigService,
    private readonly usersService: UsersService,
  ) {
    const secret = configService.get<string>('jwt.secret');
    if (!secret) {
      throw new Error('JWT_SECRET is not configured');
    }

    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: secret,
      algorithms: ['HS256'],
      passReqToCallback: false,
    });
  }

  async validate(payload: JwtPayload): Promise<unknown> {
    const { sub: userId, email } = payload;

    try {
      const user = await this.usersService.findById(userId);

      if (!user) {
        this.logger.warn(`JWT validation: User not found for ID ${userId}`);
        throw new UnauthorizedException('User not found');
      }

      if (!user.isActive) {
        this.logger.warn(`JWT validation: User ${userId} is inactive`);
        throw new UnauthorizedException('Account is disabled');
      }

      return {
        id: user.id,
        email: user.email,
        roles: user.roles,
        firstName: user.firstName,
        lastName: user.lastName,
      };
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        throw error;
      }
      this.logger.error(`JWT validation error: ${error}`);
      throw new UnauthorizedException('Invalid token');
    }
  }
}