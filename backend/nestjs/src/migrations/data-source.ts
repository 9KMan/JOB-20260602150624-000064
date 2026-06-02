import { DataSource } from 'typeorm';
import { dataSourceOptions } from '../src/config/typeorm.config';

const dataSource = new DataSource(dataSourceOptions);

dataSource
  .initialize()
  .then(() => {
    console.log('Data Source has been initialized!');
  })
  .catch((error) => {
    console.error('Error initializing data source:', error);
  });

export default dataSource;