import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ExecutionUpdateComponent } from './execution-update.component';

describe('ExecutionUpdateComponent', () => {
  let component: ExecutionUpdateComponent;
  let fixture: ComponentFixture<ExecutionUpdateComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ExecutionUpdateComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ExecutionUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
