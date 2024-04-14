import {
    Button,
    Card,
    Col,
    Collapse,
    CollapseProps,
    Empty,
    Row,
    Spin,
    Statistic,
    Typography,
    message,
} from 'antd';
import { observer } from 'mobx-react-lite';
import { useEffect, useState } from 'react';
import { Result } from '../api/models';
import AnomalyApiService from '../api/AnomalyApiService';
import {
    AnomalyStatus,
    AnomalyType,
    anomalyClassRegistry,
    anomalyStatusRegistry,
    anomalyTypeRegistry,
} from '../api/constants';
import AnomaliesTree from '../components/AnomaliesTree';
import AnomalyCard from '../components/AnomalyCard';
import AnomalyTypesChart from '../components/AnomalyTypesChart';
import { useStores } from '../hooks/useStores';

type Props = {
    reportId: number;
};

const Report = observer(({ reportId }: Props) => {
    const [result, setResult] = useState<Result | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isLoadingInitially, setIsLoadingInitially] = useState<boolean>(true);
    const [messageApi, contextHolder] = message.useMessage();
    const [isCancelLoading, setIsCancelLoading] = useState<boolean>(false);
    const { rootStore } = useStores();

    useEffect(() => {
        rootStore.clearSelectedAnomalyIds();

        const fetchData = async () => {
            try {
                if (!reportId) {
                    return;
                }

                setIsLoading(true);

                await AnomalyApiService.getResult(+reportId)
                    .then(async (result) => {
                        setResult(result);

                        if (result.status === AnomalyStatus.PROCESSING) {
                            setTimeout(() => {
                                fetchData();
                                return;
                            }, 1000);
                        } else if (result.status === AnomalyStatus.ERROR) {
                            messageApi.error('Ошибка обработки файла');
                            setIsLoading(false);
                        } else if (result.status === AnomalyStatus.SUCCESS) {
                            messageApi.success('Файл успешно обработан');
                            setIsLoading(false);
                        } else if (result.status === AnomalyStatus.CANCELED) {
                            messageApi.info('Обработка файла отменена');
                            setIsLoading(false);
                        }

                        return result;
                    })
                    .finally(() => {
                        setIsLoadingInitially(false);
                    });
            } catch (error) {
                setIsLoading(false);
                if (result) {
                    result.status = AnomalyStatus.ERROR;
                }
                messageApi.error('Ошибка загрузки данных');
                console.error(error);
            }
        };

        fetchData();
    }, [reportId, messageApi, rootStore]);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(`${window.location.origin}/report/${reportId}`);
        messageApi.success('Ссылка на отчет скопирована в буфер обмена');
    };

    const getItems = (): CollapseProps['items'] => {
        if (!result) {
            return [];
        }

        return result.anomalies?.map((anomaly, index) => {
            return {
                key: index,
                label:
                    (result.type === AnomalyType.VIDEO
                        ? `${rootStore.convertSecondsToMinutesAndSeconds(anomaly.ts)}`
                        : `Время: ${new Date(anomaly.ts).toLocaleTimeString()}`) +
                        '. Тип аномалии: ' +
                        anomalyClassRegistry[anomaly.class] ?? 'Неизвестный тип',
                children: <AnomalyCard anomaly={anomaly} />,
            };
        });
    };

    const cancelRequest = async () => {
        if (!reportId) {
            return;
        }

        setIsCancelLoading(true);

        await AnomalyApiService.cancel(+reportId)
            .then(() => {
                messageApi.info('Обработка файла отменена');
            })
            .catch(() => {
                messageApi.error('Ошибка отмены обработки файла');
            })
            .finally(() => {
                setIsCancelLoading(false);
            });
    };

    const downloadCsvReport = async () => {
        if (!reportId) {
            return;
        }

        const link = document.createElement('a');
        link.href = generateReport() ?? '';
        link.download = `report-${reportId}.csv`;
        link.click();
    };

    const generateReport = () => {
        if (!result) {
            return;
        }

        const rows = [['Время', 'Тип аномалии', 'Ссылка на артефакт']].concat(
            result.anomalies.map((anomaly) => {
                return [
                    result.type === AnomalyType.VIDEO
                        ? rootStore.convertSecondsToMinutesAndSeconds(anomaly.ts)
                        : new Date(anomaly.ts).toLocaleTimeString(),
                    anomalyClassRegistry[anomaly.class] ?? 'Неизвестный тип',
                    anomaly.link.length > 0 ? anomaly.link[0] : '',
                ];
            })
        );

        const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((e) => e.join(',')).join('\n');

        return encodeURI(csvContent);
    };

    return (
        <>
            {contextHolder}

            <Spin spinning={isLoadingInitially}>
                {result && (
                    <div>
                        <Row gutter={[16, 16]}>
                            <Col xs={{ span: 24 }} md={{ span: 12 }}>
                                <Card bordered={false}>
                                    <Statistic
                                        title='Тип файла'
                                        value={
                                            anomalyTypeRegistry[result.type] ?? 'Неизвестный тип'
                                        }
                                        precision={0}
                                    />
                                </Card>
                            </Col>
                            <Col xs={{ span: 24 }} md={{ span: 12 }}>
                                <Card bordered={false}>
                                    <Statistic
                                        title='Статус'
                                        value={
                                            anomalyStatusRegistry[result.status] ??
                                            'Неизвестный тип'
                                        }
                                        precision={0}
                                        prefix={
                                            result.status === AnomalyStatus.SUCCESS
                                                ? '✅'
                                                : result.status === AnomalyStatus.ERROR
                                                ? '❌'
                                                : result.status === AnomalyStatus.CANCELED
                                                ? '❕'
                                                : '⏳'
                                        }
                                    />
                                </Card>
                            </Col>
                        </Row>

                        <Row style={{ marginTop: 30 }}>
                            <Col xs={{ span: 24 }}>
                                {isLoading ? (
                                    <Row gutter={[16, 16]} align={'middle'}>
                                        <Col>
                                            <Spin size='default' />
                                        </Col>

                                        <Col>Обработка файла...</Col>

                                        <Col>
                                            <Button
                                                onClick={() => cancelRequest()}
                                                danger
                                                loading={isCancelLoading}
                                            >
                                                Отменить обработку файла
                                            </Button>
                                        </Col>
                                    </Row>
                                ) : result.status === AnomalyStatus.SUCCESS ||
                                  result.status === AnomalyStatus.CANCELED ? (
                                    <Row gutter={[16, 16]}>
                                        <Col>
                                            <Button onClick={() => copyToClipboard()}>
                                                Скопировать ссылку на отчет
                                            </Button>
                                        </Col>

                                        <Col>
                                            <Button
                                                onClick={() => downloadCsvReport()}
                                                type='primary'
                                            >
                                                Скачать отчет (.csv)
                                            </Button>
                                        </Col>
                                    </Row>
                                ) : (
                                    ''
                                )}
                            </Col>
                        </Row>

                        <Row style={{ marginTop: 40 }} className='report__files' gutter={[20, 20]}>
                            <Col xs={{ span: 24 }} lg={{ span: 6 }}>
                                <AnomaliesTree
                                    anomalies={result?.anomalies}
                                    anomalyType={result?.type}
                                    isLoading={isLoading}
                                />
                            </Col>
                            <Col xs={{ span: 24 }} lg={{ span: 18 }}>
                                {result?.anomalies.length > 0 ? (
                                    <Collapse
                                        defaultActiveKey={['1']}
                                        activeKey={rootStore.selectedAnomalyIdsArray}
                                        expandIconPosition={'start'}
                                        items={getItems()}
                                        onChange={(selectedKeys) => {
                                            rootStore.setSelectedAnomalyIds(selectedKeys);
                                        }}
                                    />
                                ) : (
                                    <Empty
                                        description={<span>Пока не найдено ни одной аномалии</span>}
                                    />
                                )}
                            </Col>
                        </Row>
                    </div>
                )}

                {result && result.status === AnomalyStatus.SUCCESS && (
                    <>
                        <Row style={{ marginTop: 40 }}>
                            <Typography.Title level={4}>Статистика по аномалиям</Typography.Title>
                        </Row>
                        <Row style={{ marginTop: 20 }}>
                            <Col xs={{ span: 24 }} style={{ maxHeight: 400 }}>
                                <AnomalyTypesChart anomalies={result.anomalies} />.
                            </Col>
                        </Row>
                    </>
                )}
            </Spin>
        </>
    );
});

export default Report;
