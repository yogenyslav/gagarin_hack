import {
    Breadcrumb,
    Button,
    Card,
    Col,
    Collapse,
    CollapseProps,
    Layout,
    Row,
    Spin,
    Statistic,
    Typography,
    message,
} from 'antd';
import { Content } from 'antd/es/layout/layout';
import HeaderLayout from '../components/HeaderLayout';
import { observer } from 'mobx-react-lite';
import { useParams } from 'react-router-dom';
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

const Report = observer(() => {
    const { reportId } = useParams();
    const [result, setResult] = useState<Result | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isLoadingInitially, setIsLoadingInitially] = useState<boolean>(true);
    const [messageApi, contextHolder] = message.useMessage();
    const [isCancelLoading, setIsCancelLoading] = useState<boolean>(false);

    useEffect(() => {
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
                            }, 1000);
                        } else if (result.status === AnomalyStatus.ERROR) {
                            messageApi.error('Ошибка обработки файла');
                        } else if (result.status === AnomalyStatus.SUCCESS) {
                            messageApi.success('Файл успешно обработан');
                        } else if (result.status === AnomalyStatus.CANCELED) {
                            messageApi.info('Обработка файла отменена');
                        }

                        return result;
                    })
                    .finally(() => {
                        setIsLoading(false);
                        setIsLoadingInitially(false);
                    });
            } catch (error) {
                console.error(error);
            }
        };

        fetchData();
    }, [reportId, messageApi]);

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
                        ? `Секунда ${anomaly.ts}`
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
                        ? anomaly.ts.toString()
                        : new Date(anomaly.ts).toLocaleTimeString(),
                    anomalyClassRegistry[anomaly.class] ?? 'Неизвестный тип',
                    anomaly.link,
                ];
            })
        );

        const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((e) => e.join(',')).join('\n');

        return encodeURI(csvContent);
    };

    return (
        <>
            {contextHolder}
            <Layout>
                <HeaderLayout />

                <Content className='site-layout' style={{ padding: '0 15px' }}>
                    <Breadcrumb style={{ margin: '16px 0' }}>
                        <Breadcrumb.Item>Отчет</Breadcrumb.Item>
                    </Breadcrumb>
                    <div
                        className='content'
                        style={{ padding: 24, minHeight: 380, background: '#ffffff' }}
                    >
                        <Typography.Title level={2}>Отчет</Typography.Title>
                        <Spin spinning={isLoadingInitially}>
                            {result && (
                                <div>
                                    <Row gutter={[16, 16]}>
                                        <Col xs={{ span: 24 }} md={{ span: 12 }}>
                                            <Card bordered={false}>
                                                <Statistic
                                                    title='Тип файла'
                                                    value={
                                                        anomalyTypeRegistry[result.type] ??
                                                        'Неизвестный тип'
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
                                                            : result.status ===
                                                              AnomalyStatus.CANCELED
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
                                            ) : (
                                                result &&
                                                result.status === AnomalyStatus.SUCCESS && (
                                                    <Row gutter={[16, 16]}>
                                                        <Col>
                                                            <Button
                                                                onClick={() => copyToClipboard()}
                                                            >
                                                                Скопировать ссылку на отчет
                                                            </Button>
                                                        </Col>

                                                        <Col>
                                                            <Button
                                                                onClick={() => downloadCsvReport()}
                                                                type='primary'
                                                            >
                                                                Скачать отчет
                                                            </Button>
                                                        </Col>
                                                    </Row>
                                                )
                                            )}
                                        </Col>
                                    </Row>

                                    <Row
                                        style={{ marginTop: 40 }}
                                        className='report__files'
                                        gutter={[20, 20]}
                                    >
                                        <Col xs={{ span: 24 }} lg={{ span: 6 }}>
                                            <AnomaliesTree
                                                anomalies={result?.anomalies}
                                                anomalyType={result?.type}
                                                isLoading={isLoading}
                                            />
                                        </Col>
                                        <Col xs={{ span: 24 }} lg={{ span: 18 }}>
                                            <Collapse
                                                defaultActiveKey={['1']}
                                                expandIconPosition={'start'}
                                                items={getItems()}
                                            />
                                        </Col>
                                    </Row>
                                </div>
                            )}
                        </Spin>
                    </div>
                </Content>
            </Layout>
        </>
    );
});

export default Report;
