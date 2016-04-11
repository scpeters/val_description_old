#!/usr/bin/env python

import unittest
import glob
import os
import CoeffSchemaDefinitions as coeffSchemaDefinitions
import CoeffCollectionDefinitions as coeffCollectionDefinitions
from lxml import etree as xmlParser
import lxml
import logging


class coeffFileTests(unittest.TestCase):

    def setUp(self):
        self.catkinWorkspaceDirectory = os.getenv("VAL_WORKSPACE")

        # Define the directories that coeffs live in
        self.actuatorCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/actuators'
        self.classCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/class'
        self.controllerCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/controllers'
        self.locationCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/location'
        self.modesCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/modes'
        self.safetyCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/safety'
        self.sensorCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/sensors'

        self.log = logging.getLogger("Coeff Test Logger")
        self.correctFiles = []
        self.incorrectFiles = []

    def tearDown(self):
        pass

    def getSchemaParser(self, schema_definition):
        schema_root = xmlParser.XML(schema_definition)
        schema = xmlParser.XMLSchema(schema_root)
        return xmlParser.XMLParser(schema=schema)

    def checkForDuplicates(self, directory):
        # Assemble the schema
        os.chdir(directory)
        for coeffFile in glob.glob("*.xml"):
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                for coeff in xmlCoeffObject.iter('Coeff'):
                    coeffNames.append(coeff.get('id'))
                if len(coeffNames) != len(set(coeffNames)):
                    raise Exception
            except Exception:
                self.log.error(coeffFile + " has duplicate coeffs")
                self.incorrectFiles.append(coeffFile)
        assert len(self.incorrectFiles) == 0

    def checkForNeeded(self, directory, neededCoeffs):
        # Assemble the schema
        os.chdir(directory)
        for coeffFile in glob.glob("*.xml"):
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                for coeff in xmlCoeffObject.iter('Coeff'):
                    coeffNames.append(coeff.get('id'))
                for coeff in neededCoeffs:
                    if coeff not in coeffNames:
                        raise Exception
            except Exception:
                self.log.error(coeffFile + " is missing a needed coeff " + coeff)
                self.incorrectFiles.append(coeffFile)
        assert len(self.incorrectFiles) == 0

    def checkValidSchema(self, schema, directory, checkOnlyHClass=False):
        parser = self.getSchemaParser(schema)
        os.chdir(directory)
        for coeffFile in glob.glob("*.xml"):
            if 'test' not in coeffFile:  # Don't check the test files
                if checkOnlyHClass and 'v_h_' in coeffFile or not checkOnlyHClass and 'v_h_' not in coeffFile:
                    try:
                        root = xmlParser.parse(coeffFile, parser)
                        self.correctFiles.append(coeffFile)
                    except xmlParser.XMLSyntaxError:
                        self.log.error(coeffFile + " has coeffs that are not in the schema")
                        self.incorrectFiles.append(coeffFile)

        assert len(self.incorrectFiles) == 0

    ####################################################################################
    #    Check that actuator coeff files only have coeffs that should be in them.      #
    ####################################################################################
    def testActuatorCoeffsValidSchema(self):
        # Assemble the schema
        schemaNoClassH = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.actuator_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.actuator_coeff_files_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
        self.checkValidSchema(schemaNoClassH, self.actuatorCoeffDirectory)

        schemaForClassH = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.athena_actuator_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
        self.checkValidSchema(schemaForClassH, self.actuatorCoeffDirectory, True)

    ####################################################################################
    #    Check that actuator coeff files have no duplicate coeffs.                     #
    ####################################################################################
    def testActuatorNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.actuatorCoeffDirectory)

    ####################################################################################
    #    Check that actuator coeff files have coeffs that need to be in them.          #
    ####################################################################################
    def testActuatorEssentialCoeffs(self):
        self.checkForNeeded(self.actuatorCoeffDirectory, coeffCollectionDefinitions.ActuatorNeededCoeffs)

    # ####################################################################################
    # #    Check that class coeff files only have coeffs that should be in them.         #
    # ####################################################################################
    # def testClassCoeffsValidSchema(self):
    #     # Assemble the schema
    #     schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.class_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.actuator_class_info_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
    #     self.checkValidSchema(schema, self.classCoeffDirectory)

    # ####################################################################################
    # #    Check that class coeff files have no duplicate coeffs.                        #
    # ####################################################################################
    # def testClassNoDuplicateCoeffs(self):
    #     self.checkForDuplicates(self.classCoeffDirectory)

    # ####################################################################################
    # #    Check that class coeff files have coeffs that need to be in them.             #
    # ####################################################################################
    # def testClassEssentialCoeffs(self):
    #     self.checkForNeeded(self.classCoeffDirectory, coeffCollectionDefinitions.ClassNeededCoeffs)

    # ####################################################################################
    # #    Check that controller coeff files only have coeffs that should be in them.    #
    # ####################################################################################
    # def testControllerCoeffsValidSchema(self):
    #     # Assemble the schema
    #     schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.controller_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
    #     self.checkValidSchema(schema, self.controllerCoeffDirectory)

    # ####################################################################################
    # #    Check that controller coeff files have no duplicate coeffs.                   #
    # ####################################################################################
    # def testControllerNoDuplicateCoeffs(self):
    #     self.checkForDuplicates(self.controllerCoeffDirectory)

    # ####################################################################################
    # #    Check that controller coeff files have coeffs that need to be in them.        #
    # ####################################################################################
    # def testControllerEssentialCoeffs(self):
    #     self.checkForNeeded(self.controllerCoeffDirectory, coeffCollectionDefinitions.ControllerNeededCoeffs)

    # ####################################################################################
    # #    Check that location coeff files only have coeffs that should be in them.      #
    # ####################################################################################
    # def testLocationCoeffsValidSchema(self):
    #     # Assemble the schema
    #     schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.location_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
    #     self.checkValidSchema(schema, self.controllerCoeffDirectory)

    # ####################################################################################
    # #    Check that location coeff files have no duplicate coeffs.                     #
    # ####################################################################################
    # def testLocationNoDuplicateCoeffs(self):
    #     self.checkForDuplicates(self.locationCoeffDirectory)

    # ####################################################################################
    # #    Check that location coeff files have coeffs that need to be in them.          #
    # ####################################################################################
    # def testLocationEssentialCoeffs(self):
    #     self.checkForNeeded(self.locationCoeffDirectory, coeffCollectionDefinitions.LocationNeededCoeffs)

    # ####################################################################################
    # #    Check that mode coeff files only have coeffs that should be in them.          #
    # ####################################################################################
    # def testModesCoeffsValidSchema(self):
    #     # Assemble the schema
    #     schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.modes_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
    #     self.checkValidSchema(schema, self.controllerCoeffDirectory)

    # ####################################################################################
    # #    Check that mode coeff files have no duplicate coeffs.                         #
    # ####################################################################################
    # def testModeNoDuplicateCoeffs(self):
    #     self.checkForDuplicates(self.modesCoeffDirectory)

    # ####################################################################################
    # #    Check that mode coeff files have coeffs that need to be in them.              #
    # ####################################################################################
    # def testModeEssentialCoeffs(self):
    #     self.checkForNeeded(self.modesCoeffDirectory, coeffCollectionDefinitions.ModesNeededCoeffs)

    # ####################################################################################
    # #    Check that safety coeff files only have coeffs that should be in them.        #
    # ####################################################################################
    # def testSafetyCoeffsValidSchema(self):
    #     # Assemble the schema
    #     schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.safety_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
    #     self.checkValidSchema(schema, self.controllerCoeffDirectory)

    # ####################################################################################
    # #    Check that safety coeff files have no duplicate coeffs.                       #
    # ####################################################################################
    # def testSafetyNoDuplicateCoeffs(self):
    #     self.checkForDuplicates(self.safetyCoeffDirectory)

    # ####################################################################################
    # #    Check that safety coeff files have coeffs that need to be in them.            #
    # ####################################################################################
    # def testSafetyEssentialCoeffs(self):
    #     self.checkForNeeded(self.safetyCoeffDirectory, coeffCollectionDefinitions.SafetyNeededCoeffs)

    # ####################################################################################
    # #    Check that sensor coeff files only have coeffs that should be in them.        #
    # ####################################################################################
    # def testSensorCoeffsValidSchema(self):
    #     # Assemble the schema
    #     schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.sensor_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
    #     self.checkValidSchema(schema, self.controllerCoeffDirectory)

    # ####################################################################################
    # #    Check that sensor coeff files have no duplicate coeffs.                       #
    # ####################################################################################
    # def testSensorNoDuplicateCoeffs(self):
    #     self.checkForDuplicates(self.sensorCoeffDirectory)

    # ####################################################################################
    # #    Check that sensor coeff files have coeffs that need to be in them.            #
    # ####################################################################################
    # def testSensorEssentialCoeffs(self):
    #     self.checkForNeeded(self.sensorCoeffDirectory, coeffCollectionDefinitions.SensorNeededCoeffs)
