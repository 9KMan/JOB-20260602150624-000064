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
import { ListingsService } from './listings.service';
import { CreateListingDto, UpdateListingDto, SearchListingsDto } from './dto/create-listing.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { RolesGuard } from '../auth/roles.guard';
import { Roles } from '../auth/roles.decorator';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { UserRole } from '../users/entities/user.entity';
import { ListingStatus } from './entities/listing.entity';

@ApiTags('listings')
@Controller('listings')
export class ListingsController {
  private readonly logger = new Logger(ListingsController.name);

  constructor(private readonly listingsService: ListingsService) {}

  @Post()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({ summary: 'Create a new listing' })
  @ApiResponse({ status: 201, description: 'Listing created successfully' })
  @ApiResponse({ status: 400, description: 'Validation error' })
  async create(
    @Body() createListingDto: CreateListingDto,
    @CurrentUser() user: { id: string },
  ) {
    this.logger.log(`Creating listing for user: ${user.id}`);
    return this.listingsService.create(createListingDto, user.id);
  }

  @Get()
  @ApiOperation({ summary: 'Get all listings with optional filtering' })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiQuery({ name: 'offset', required: false, type: Number })
  @ApiQuery({ name: 'status', required: false, enum: ListingStatus })
  @ApiResponse({ status: 200, description: 'List of listings' })
  async findAll(
    @Query('limit') limit?: number,
    @Query('offset') offset?: number,
    @Query('status') status?: ListingStatus,
  ) {
    return this.listingsService.findAll({ limit, offset, status });
  }

  @Get('search')
  @ApiOperation({ summary: 'Search listings with filters' })
  @ApiResponse({ status: 200, description: 'Search results' })
  async search(@Query() searchDto: SearchListingsDto) {
    return this.listingsService.search(searchDto);
  }

  @Get('featured')
  @ApiOperation({ summary: 'Get featured listings' })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiResponse({ status: 200, description: 'Featured listings' })
  async getFeatured(@Query('limit') limit?: number) {
    return this.listingsService.findFeatured(limit);
  }

  @Get('category/:category')
  @ApiOperation({ summary: 'Get listings by category' })
  @ApiParam({ name: 'category', enum: ['PLUMBING', 'ELECTRICAL', 'HVAC', 'CLEANING'] })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  @ApiResponse({ status: 200, description: 'Listings in category' })
  async findByCategory(
    @Param('category') category: string,
    @Query('limit') limit?: number,
  ) {
    return this.listingsService.findByCategory(category as any, limit);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get listing by ID' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Listing details' })
  @ApiResponse({ status: 404, description: 'Listing not found' })
  async findOne(@Param('id') id: string) {
    const listing = await this.listingsService.findByIdOrFail(id);
    await this.listingsService.incrementViewCount(id);
    return listing;
  }

  @Get('owner/me')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({ summary: 'Get current user\'s listings' })
  @ApiResponse({ status: 200, description: 'User listings' })
  async findMyListings(
    @CurrentUser() user: { id: string },
    @Query('limit') limit?: number,
    @Query('offset') offset?: number,
  ) {
    return this.listingsService.findByOwner(user.id, { limit, offset });
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @ApiOperation({ summary: 'Update a listing' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Listing updated successfully' })
  @ApiResponse({ status: 404, description: 'Listing not found' })
  async update(
    @Param('id') id: string,
    @Body() updateListingDto: UpdateListingDto,
    @CurrentUser() user: { id: string; roles: string[] },
  ) {
    const isAdmin = user.roles.includes(UserRole.ADMIN);
    this.logger.log(`Updating listing: ${id}`);
    return this.listingsService.update(
      id,
      updateListingDto,
      isAdmin ? undefined : user.id,
    );
  }

  @Patch(':id/status')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @Roles(UserRole.ADMIN, UserRole.MODERATOR)
  @ApiOperation({ summary: 'Update listing status (admin/moderator only)' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Status updated' })
  @ApiResponse({ status: 404, description: 'Listing not found' })
  async updateStatus(
    @Param('id') id: string,
    @Body() body: { status: ListingStatus },
  ) {
    this.logger.log(`Updating listing status: ${id} to ${body.status}`);
    return this.listingsService.updateStatus(id, body.status);
  }

  @Patch(':id/featured')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @Roles(UserRole.ADMIN)
  @ApiOperation({ summary: 'Set listing featured status (admin only)' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Featured status updated' })
  async setFeatured(
    @Param('id') id: string,
    @Body() body: { isFeatured: boolean },
  ) {
    this.logger.log(`Setting listing ${id} featured: ${body.isFeatured}`);
    return this.listingsService.setFeatured(id, body.isFeatured);
  }

  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('JWT-auth')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Delete a listing' })
  @ApiParam({ name: 'id', format: 'uuid' })
  @ApiResponse({ status: 200, description: 'Listing deleted successfully' })
  @ApiResponse({ status: 404, description: 'Listing not found' })
  async delete(
    @Param('id') id: string,
    @CurrentUser() user: { id: string; roles: string[] },
  ) {
    const isAdmin = user.roles.includes(UserRole.ADMIN);
    this.logger.log(`Deleting listing: ${id}`);
    await this.listingsService.delete(id, isAdmin ? undefined : user.id);
    return { message: 'Listing deleted successfully' };
  }
}