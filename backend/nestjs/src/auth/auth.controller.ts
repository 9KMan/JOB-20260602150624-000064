import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiBearerAuth,
  ApiBody,
} from '@nestjs/swagger';
import { AuthService, AuthResponse, TokenPair } from './auth.service';
import { LoginDto, LogoutDto, RefreshTokenDto } from './dto/login.dto';
import { RegisterDto } from './dto/login.dto';

@ApiTags('auth')
@Controller('auth')
export class AuthController {
  private readonly logger = new Logger(AuthController.name);

  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @ApiOperation({ summary: 'Register a new user' })
  @ApiResponse({
    status: 201,
    description: 'User successfully registered',
    type: AuthResponse,
  })
  @ApiResponse({ status: 400, description: 'Email already registered' })
  @ApiResponse({ status: 400, description: 'Validation error' })
  async register(@Body() registerDto: RegisterDto): Promise<AuthResponse> {
    this.logger.log(`Registration attempt for: ${registerDto.email}`);
    return this.authService.register(registerDto);
  }

  @Post('login')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Login with email and password' })
  @ApiResponse({
    status: 200,
    description: 'User successfully logged in',
    type: AuthResponse,
  })
  @ApiResponse({ status: 401, description: 'Invalid credentials' })
  @ApiResponse({ status: 400, description: 'Validation error' })
  async login(@Body() loginDto: LoginDto): Promise<AuthResponse> {
    this.logger.log(`Login attempt for: ${loginDto.email}`);
    return this.authService.login(loginDto);
  }

  @Post('refresh')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Refresh access token' })
  @ApiResponse({
    status: 200,
    description: 'New access token generated',
    type: TokenPair,
  })
  @ApiResponse({ status: 401, description: 'Invalid refresh token' })
  @ApiBody({ type: RefreshTokenDto })
  async refreshToken(
    @Body() refreshTokenDto: RefreshTokenDto,
  ): Promise<TokenPair> {
    this.logger.log('Token refresh attempt');
    return this.authService.refreshToken(refreshTokenDto.refreshToken);
  }

  @Post('logout')
  @HttpCode(HttpStatus.OK)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({ summary: 'Logout and invalidate token' })
  @ApiResponse({ status: 200, description: 'Successfully logged out' })
  @ApiResponse({ status: 401, description: 'Not authenticated' })
  async logout(
    @Body() logoutDto: LogoutDto,
  ): Promise<{ message: string }> {
    const userId = 'current-user-id';
    await this.authService.logout(userId);
    return { message: 'Successfully logged out' };
  }
}