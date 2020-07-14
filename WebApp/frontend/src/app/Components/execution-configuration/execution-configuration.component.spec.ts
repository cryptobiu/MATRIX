import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ExecutionConfigurationComponent } from './execution-configuration.component';

describe('ExecutionConfigurationComponent', () => {
  let component: ExecutionConfigurationComponent;
  let fixture: ComponentFixture<ExecutionConfigurationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ExecutionConfigurationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ExecutionConfigurationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
