import { Injectable } from '@angular/core';
import {Client} from 'elasticsearch-browser';

@Injectable({
  providedIn: 'root'
})
export class ElasticsearchService {

  private esClient: Client;

  constructor() {
    if(!this.esClient)
    {
      this.esClient = new Client({
        host: '3.81.191.221:9200',
        log: 'trace',
        use_ssl: true
      });
    }
  }

  getDocuments(_index, _type, protocolName): any {

    let requestBody = {
      'query': {
        'bool': {
          'must': [
            { 'match' : { 'protocolName': protocolName }}
          ],
          'filter': [
            { 'range': { 'timestamp': { 'gte': 'now-3m/m', 'lt': 'now' } } }
          ]
        }
      }
    };
    return this.esClient.search({
      index: _index,
      type: _type,
      body:requestBody,
      filterPath: ['hits.hits._source']
    });

  }
}
