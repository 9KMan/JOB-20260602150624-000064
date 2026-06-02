import {
  Injectable,
  ExecutionContext,
  UnauthorizedException,
  Logger,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  private readonly logger = new Logger(JwtAuthGuard.name);

  canActivate(context: ExecutionContext) {
    return super.canActivate(context);
  }

  handleRequest<TUser = unknown>(
    err: Error | null,
    user: TUser | false,
    info: Error | undefined,
  ): TUser {
    if (err || !user) {
      const message = info?.message || err?.message || 'Unauthorized';

      this.logger.warn(`JWT Auth Guard failed: ${message}`);

      if (message.includes('expired')) {
        throw new UnauthorizedException('Token has expired');
      }
      if (message.includes('invalid')) {
        throw new UnauthorizedException('Invalid token');
      }
      if (message.includes('No auth token')) {
        throw new UnauthorizedException('No authentication token provided');
      }

      throw new UnauthorizedException('Authentication required');
    }

    return user;
  }
}