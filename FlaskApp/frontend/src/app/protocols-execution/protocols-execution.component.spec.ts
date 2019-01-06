import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProtocolsExecutionComponent } from './protocols-execution.component';

describe('ProtocolsExecutionComponent', () => {
  let component: ProtocolsExecutionComponent;
  let fixture: ComponentFixture<ProtocolsExecutionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProtocolsExecutionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProtocolsExecutionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
