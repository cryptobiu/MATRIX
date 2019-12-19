import {Injectable, ErrorHandler, Injector} from '@angular/core';
import {Router} from '@angular/router';

@Injectable()
export class GlobalErrorHandlerService  implements ErrorHandler {

  constructor(private injector: Injector) { }

  handleError(error: any): void {
    const router = this.injector.get(Router);
    console.error('Error: ' + error);
    router.navigate(['/error']);
  }
}
