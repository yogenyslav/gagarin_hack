import { Card, Tree, Input } from 'antd';
import React from 'react';

import type { DataNode } from 'antd/es/tree';

const { Search } = Input;

type Props = {
    anomalies: unknown[];
};

const Anomalies = ({ anomalies }: Props) => {
    const [searchValue, setSearchValue] = React.useState('');

    const getTreeData = (): DataNode[] => {
        return anomalies
            ?.filter(() => {
                return 'file.filename'.includes(searchValue);
            })
            .map((file, index) => {
                return {
                    title: 'file.filename',
                    key: index,
                };
            });
    };

    return (
        <>
            <Card className='file-list' title='Файлы' bordered={true} style={{ width: 300 }}>
                <div>
                    <Search
                        style={{ marginBottom: 8 }}
                        placeholder='Поиск'
                        onChange={(event) => setSearchValue(event.target.value)}
                    />
                    <Tree
                        onSelect={([selectedKeys]) => {
                            console.log(selectedKeys);
                        }}
                        showLine={true}
                        treeData={getTreeData()}
                    />
                </div>
            </Card>
        </>
    );
};

export default Anomalies;
