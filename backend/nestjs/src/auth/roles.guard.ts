import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
  ForbiddenException,
  Logger,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { UserRole } from '../../users/entities/user.entity';
import { ROLES_KEY } from '../roles.decorator';

@Injectable()
export class RolesGuard implements CanActivate {
  private readonly logger = new Logger(RolesGuard.name);

  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<UserRole[]>(
      ROLES_KEY,
      [context.getHandler(), context.getClass()],
    );

    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const user = request.user;

    if (!user) {
      this.logger.warn('Roles guard: No user found in request');
      throw new UnauthorizedException('User not authenticated');
    }

    const userRoles = user.roles || [];
    const hasRole = requiredRoles.some((role) => userRoles.includes(role));

    if (!hasRole) {
      this.logger.warn(
        `Roles guard: User ${user.id} does not have required roles: ${requiredRoles.join(', ')}`,
      );
      throw new ForbiddenException(
        'You do not have permission to access this resource',
      );
    }

    return true;
  }
}