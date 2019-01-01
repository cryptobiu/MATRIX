import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProtocolsDetailsComponent } from './protocols-details.component';

describe('ProtocolsDetailsComponent', () => {
  let component: ProtocolsDetailsComponent;
  let fixture: ComponentFixture<ProtocolsDetailsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProtocolsDetailsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProtocolsDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
