class Status:
    @staticmethod
    def getStatusArray(framework):
        if framework is 'Hadoop':
            return [
                "setting up environment",
                "downloading Hadoop",
                "downloading JDK",
                "copying files to nodes",
                "unpacking Hadoop on nodes",
                "unpacking JDK on nodes",
                "perform last configuration steps",
                "Hadoop Cluster is ready"
            ]
