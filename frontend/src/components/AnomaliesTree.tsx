import { Card, Skeleton, Tree } from 'antd';
import type { DataNode } from 'antd/es/tree';
import { Anomaly } from '../api/models';
import { AnomalyType, anomalyClassRegistry } from '../api/constants';
import { useStores } from '../hooks/useStores';
import { observer } from 'mobx-react-lite';

type Props = {
    anomalies: Anomaly[];
    anomalyType: AnomalyType;
    isLoading: boolean;
};

const AnomaliesTree = observer(({ anomalies, anomalyType, isLoading }: Props) => {
    const { rootStore } = useStores();

    const getTreeData = (): DataNode[] => {
        return anomalies.map((anomaly, index) => {
            return {
                title:
                    (anomalyType === AnomalyType.VIDEO
                        ? `${rootStore.convertSecondsToMinutesAndSeconds(anomaly.ts)}`
                        : `Время: ${new Date(anomaly.ts).toLocaleTimeString()}`) +
                    ` (${anomalyClassRegistry[anomaly.class] ?? ''})`,
                key: index,
            };
        });
    };

    return (
        <>
            <Card className='file-list' title='Таймкоды' bordered={true}>
                <div>
                    <Tree
                        onSelect={(selectedKeys) => {
                            console.log(selectedKeys);
                            rootStore.setSelectedAnomalyId(selectedKeys.toString());
                        }}
                        selectedKeys={rootStore.selectedAnomalyIdsArray}
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
});

export default AnomaliesTree;
