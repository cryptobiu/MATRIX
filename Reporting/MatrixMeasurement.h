//
// Created by liork on 8/22/18.
//

#ifndef MATRIXMEASUREMENT_H
#define MATRIXMEASUREMENT_H

#include <string>
#include <chrono>
#include <fstream>
#include <iostream>
#include <algorithm>


using namespace std;
using namespace std::chrono;

class MatrixMeasurement
{
private:
    string getcwdStr()
    {
        char buff[256];
        auto res = getcwd(buff, 256);
        if(NULL == res)
            exit(-1);
        return string(res);
    }

    int getTaskIdx(string name)
    {
        auto it = std::find(m_tasksNames.begin(), m_tasksNames.end(), name);
        auto idx = distance(m_tasksNames.begin(), it);
        return idx;
    }

    vector<vector<long>> m_cpuStartTimes;
    vector<vector<long>> m_cpuEndTimes;
    string m_arguments = "";
    vector<string> m_tasksNames;
    int m_partiesNumber = 0;
    string m_logsPath;

public:
    MatrixMeasurement(size_t argc, char* argv[], int partiesNumber, vector<string> tasksNames, int numberOfIterations,
                      string logsPath=""):
            m_cpuStartTimes(vector<vector<long>>(tasksNames.size(), vector<long>(numberOfIterations))),
            m_cpuEndTimes(vector<vector<long>>(tasksNames.size(), vector<long>(numberOfIterations)))
    {

        for(size_t idx = 0; idx < argc; ++idx)
        {
            string s(argv[idx]);
            if (idx < argc - 1)
                m_arguments += s + "*";
            else
                m_arguments += s;
        }

        m_tasksNames = tasksNames;
        m_partiesNumber = partiesNumber;
        m_logsPath=logsPath;

    }

    void startSubTask(string taskName, int currentIterationNumber)
    {
        int taskIdx = getTaskIdx(taskName);
        auto now = system_clock::now();

        //Cast the time point to ms, then get its duration, then get the duration's count.
        auto ms = time_point_cast<milliseconds>(now).time_since_epoch().count();
        m_cpuStartTimes[taskIdx][currentIterationNumber] = ms;
    }

    void endSubTask(string taskName, int currentIterationNumber)
    {
        int taskIdx = getTaskIdx(taskName);
        auto now = system_clock::now();

        //Cast the time point to ms, then get its duration, then get the duration's count.
        auto ms = time_point_cast<milliseconds>(now).time_since_epoch().count();
        m_cpuEndTimes[taskIdx][currentIterationNumber] = ms;

        // if this is the last task and last iteration write the data to file
        if (taskIdx == m_tasksNames.size() - 1 && currentIterationNumber == m_cpuEndTimes[0].size() - 1)
        {
            if(m_logsPath.length() == 0)
                string logFileName = getcwdStr() + m_arguments + ".log";
            else
                string logFileName = m_logsPath + m_arguments + ".log";

            ofstream logFile(logFileName);
            if (logFile.is_open())
            {
                //write parties number to file
                logfile << to_string(m_partiesNumber) + "\n";

                //write to file
                int numberOfIterations = m_cpuEndTimes[0].size();
                for (size_t idx = 0; idx < m_tasksNames.size(); ++idx)
                {
                    logFile << m_tasksNames[idx] + ":";
                    cout << "taskName : " << m_tasksNames[idx] << endl;
                    for (size_t idx2 = 0; idx2 < numberOfIterations; ++idx2)
                    {
                        cout << "value : " << m_cpuEndTimes[idx][idx2] << endl;
                        logFile << to_string(m_cpuEndTimes[idx][idx2] - m_cpuStartTimes[idx][idx2])
                        + ",";
                    }

                    logFile << "\n";
                }
                logFile.close();
            }
        }
    }
};

#endif //MATRIXMEASUREMENT_H
