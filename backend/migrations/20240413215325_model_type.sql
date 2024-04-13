-- +goose Up
-- +goose StatementBegin
alter table query
    add column model int not null default 1;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
alter table query
    drop column model;
-- +goose StatementEnd
