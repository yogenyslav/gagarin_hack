import { makeAutoObservable } from 'mobx';

export class RootStore {
    constructor() {
        makeAutoObservable(this);
    }
}
