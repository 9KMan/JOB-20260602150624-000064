import {
  Injectable,
  NotFoundException,
  BadRequestException,
  Logger,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, Like, In, Between, Raw, SelectQueryBuilder } from 'typeorm';
import { Listing, ListingStatus, ListingCategory } from './entities/listing.entity';
import { CreateListingDto, UpdateListingDto, SearchListingsDto } from './dto/create-listing.dto';
import { User } from '../users/entities/user.entity';

@Injectable()
export class ListingsService {
  private readonly logger = new Logger(ListingsService.name);

  constructor(
    @InjectRepository(Listing)
    private readonly listingRepository: Repository<Listing>,
  ) {}

  async create(createListingDto: CreateListingDto, ownerId: string): Promise<Listing> {
    const listing = this.listingRepository.create({
      ...createListingDto,
      ownerId,
      status: ListingStatus.DRAFT,
    });

    const savedListing = await this.listingRepository.save(listing);

    this.logger.log(`Listing created: ${savedListing.id} by user ${ownerId}`);

    return savedListing;
  }

  async findAll(options?: {
    limit?: number;
    offset?: number;
    status?: ListingStatus;
  }): Promise<{ listings: Listing[]; total: number }> {
    const { limit = 20, offset = 0, status } = options ?? {};

    const queryBuilder = this.listingRepository
      .createQueryBuilder('listing')
      .leftJoinAndSelect('listing.owner', 'owner')
      .select([
        'listing.id',
        'listing.title',
        'listing.description',
        'listing.category',
        'listing.status',
        'listing.price',
        'listing.currency',
        'listing.location',
        'listing.contactPhone',
        'listing.contactEmail',
        'listing.isFeatured',
        'listing.viewCount',
        'listing.createdAt',
        'listing.updatedAt',
      ]);

    if (status) {
      queryBuilder.andWhere('listing.status = :status', { status });
    }

    const [listings, total] = await queryBuilder
      .orderBy('listing.createdAt', 'DESC')
      .skip(offset)
      .take(limit)
      .getManyAndCount();

    return { listings, total };
  }

  async findById(id: string): Promise<Listing | null> {
    return this.listingRepository.findOne({
      where: { id },
      relations: ['owner'],
    });
  }

  async findByIdOrFail(id: string): Promise<Listing> {
    const listing = await this.findById(id);

    if (!listing) {
      throw new NotFoundException(`Listing with ID ${id} not found`);
    }

    return listing;
  }

  async findByOwner(ownerId: string, options?: {
    limit?: number;
    offset?: number;
  }): Promise<{ listings: Listing[]; total: number }> {
    const { limit = 20, offset = 0 } = options ?? {};

    const [listings, total] = await this.listingRepository.findAndCount({
      where: { ownerId },
      order: { createdAt: 'DESC' },
      skip: offset,
      take: limit,
    });

    return { listings, total };
  }

  async search(searchDto: SearchListingsDto): Promise<{ listings: Listing[]; total: number }> {
    const {
      query,
      category,
      status = ListingStatus.ACTIVE,
      minPrice,
      maxPrice,
      location,
      limit = 20,
      offset = 0,
      sortBy = 'createdAt',
      sortOrder = 'DESC',
    } = searchDto;

    const queryBuilder = this.listingRepository
      .createQueryBuilder('listing')
      .leftJoinAndSelect('listing.owner', 'owner');

    if (status) {
      queryBuilder.andWhere('listing.status = :status', { status });
    }

    if (category) {
      queryBuilder.andWhere('listing.category = :category', { category });
    }

    if (query) {
      queryBuilder.andWhere(
        '(listing.title ILIKE :query OR listing.description ILIKE :query OR listing.tags @> ARRAY[:query]::varchar[])',
        { query: `%${query}%` },
      );
    }

    if (minPrice !== undefined) {
      queryBuilder.andWhere('listing.price >= :minPrice', { minPrice });
    }

    if (maxPrice !== undefined) {
      queryBuilder.andWhere('listing.price <= :maxPrice', { maxPrice });
    }

    if (location) {
      queryBuilder.andWhere('listing.location ILIKE :location', { location: `%${location}%` });
    }

    const validSortColumns = ['createdAt', 'price', 'viewCount', 'title'];
    const sortColumn = validSortColumns.includes(sortBy) ? sortBy : 'createdAt';

    queryBuilder
      .orderBy(`listing.${sortColumn}`, sortOrder)
      .skip(offset)
      .take(limit);

    const [listings, total] = await queryBuilder.getManyAndCount();

    return { listings, total };
  }

  async update(id: string, updateListingDto: UpdateListingDto, userId?: string): Promise<Listing> {
    const listing = await this.findByIdOrFail(id);

    if (userId && listing.ownerId !== userId) {
      throw new BadRequestException('You can only update your own listings');
    }

    const allowedUpdates: (keyof UpdateListingDto)[] = [
      'title', 'description', 'category', 'price', 'currency',
      'status', 'images', 'location', 'coordinates', 'contactPhone',
      'contactEmail', 'tags',
    ];

    for (const key of allowedUpdates) {
      if (updateListingDto[key] !== undefined) {
        (listing as Record<string, unknown>)[key] = updateListingDto[key];
      }
    }

    const updatedListing = await this.listingRepository.save(listing);

    this.logger.log(`Listing updated: ${id}`);

    return updatedListing;
  }

  async delete(id: string, userId?: string): Promise<void> {
    const listing = await this.findByIdOrFail(id);

    if (userId && listing.ownerId !== userId) {
      throw new BadRequestException('You can only delete your own listings');
    }

    await this.listingRepository.remove(listing);

    this.logger.log(`Listing deleted: ${id}`);
  }

  async incrementViewCount(id: string): Promise<void> {
    await this.listingRepository.increment({ id }, 'viewCount', 1);
  }

  async setFeatured(id: string, isFeatured: boolean): Promise<Listing> {
    const listing = await this.findByIdOrFail(id);

    listing.isFeatured = isFeatured;

    return this.listingRepository.save(listing);
  }

  async updateStatus(id: string, status: ListingStatus): Promise<Listing> {
    const listing = await this.findByIdOrFail(id);

    listing.status = status;

    return this.listingRepository.save(listing);
  }

  async findFeatured(limit = 10): Promise<Listing[]> {
    return this.listingRepository.find({
      where: { isFeatured: true, status: ListingStatus.ACTIVE },
      order: { viewCount: 'DESC' },
      take: limit,
    });
  }

  async findByCategory(category: ListingCategory, limit = 20): Promise<Listing[]> {
    return this.listingRepository.find({
      where: { category, status: ListingStatus.ACTIVE },
      order: { createdAt: 'DESC' },
      take: limit,
    });
  }
}