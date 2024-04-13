import { Card, Skeleton, Tree } from 'antd';
import type { DataNode } from 'antd/es/tree';
import { Anomaly } from '../api/models';
import { AnomalyType } from '../api/constants';

type Props = {
    anomalies: Anomaly[];
    anomalyType: AnomalyType;
    isLoading: boolean;
};

const AnomaliesTree = ({ anomalies, anomalyType, isLoading }: Props) => {
    const getTreeData = (): DataNode[] => {
        return anomalies.map((anomaly, index) => {
            return {
                title:
                    anomalyType === AnomalyType.VIDEO
                        ? `Секунда ${anomaly.ts}`
                        : `Время: ${new Date(anomaly.ts).toLocaleTimeString()}`,
                key: index,
            };
        });
    };

    return (
        <>
            <Card className='file-list' title='Таймкоды' bordered={true}>
                <div>
                    <Tree
                        onSelect={([selectedKeys]) => {
                            console.log(selectedKeys);
                        }}
                        showLine={true}
                        treeData={getTreeData()}
                    />

                    {isLoading && (
                        <Skeleton
                            style={{ marginTop: 10 }}
                            active
                            paragraph={{ rows: 4 }}
                            title={false}
                        />
                    )}
                </div>
            </Card>
        </>
    );
};

export default AnomaliesTree;
