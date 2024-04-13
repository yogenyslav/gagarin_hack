import {
    BarChart,
    Bar,
    Rectangle,
    XAxis,
    YAxis,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import { Anomaly } from '../api/models';

type Props = {
    anomalies: Anomaly[];
};

const AnomalyTypesChart = ({ anomalies }: Props) => {
    const mapAnomaliesToData = (anomalies: Anomaly[]) => {
        const anomalyTypes = anomalies.reduce((acc, anomaly) => {
            if (acc[anomaly.class]) {
                acc[anomaly.class]++;
            } else {
                acc[anomaly.class] = 1;
            }

            return acc;
        }, {} as Record<string, number>);

        return Object.entries(anomalyTypes).map(([name, anomaliesCount]) => ({
            name,
            anomaliesCount,
        }));
    };

    return (
        <>
            <ResponsiveContainer width='100%' height='100%'>
                <BarChart
                    width={500}
                    height={300}
                    data={mapAnomaliesToData(anomalies)}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                    layout='horizontal'
                >
                    <CartesianGrid strokeDasharray='3 3' />
                    <XAxis dataKey='name' />
                    <YAxis />
                    <Legend />
                    <Bar
                        dataKey='anomaliesCount'
                        fill='#82ca9d'
                        activeBar={<Rectangle fill='gold' stroke='purple' />}
                    />
                </BarChart>
            </ResponsiveContainer>
        </>
    );
};

export default AnomalyTypesChart;
