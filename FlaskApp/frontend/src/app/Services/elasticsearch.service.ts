import { Injectable } from '@angular/core';
import {Client} from 'elasticsearch-browser';
import {IDeploymentData} from "../interfaces";

@Injectable({
  providedIn: 'root'
})
export class ElasticsearchService {

  private esClient: Client;

  constructor() {
    if(!this.esClient)
    {
      this.esClient = new Client({
        host: 'https://search-escryptobiu-fyopgg3zepk6dtda4zerc53apy.us-east-1.es.amazonaws.com/',
        log: 'trace',
        use_ssl: true
      });
    }
  }

  getDocuments(_index, _type): any {

    let requestBody = {
      'query': {
        'match_all': {}
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
