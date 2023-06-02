import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material/dialog";


/**
 * Interface to structure data that is passed to the dialog
 */
export interface DialogData {
  query: string;
}


@Component({
  selector: 'app-not-found-dialog',
  templateUrl: './not-found-dialog.component.html',
  styleUrls: ['./not-found-dialog.component.css']
})
export class NotFoundDialogComponent {
  constructor(public dialogRef: MatDialogRef<NotFoundDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: DialogData){}
}
