import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProtocolsUpdateComponent } from './protocols-update.component';

describe('ProtocolsUpdateComponent', () => {
  let component: ProtocolsUpdateComponent;
  let fixture: ComponentFixture<ProtocolsUpdateComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProtocolsUpdateComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProtocolsUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
